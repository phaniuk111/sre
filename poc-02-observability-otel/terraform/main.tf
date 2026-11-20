# Observability building blocks on AWS for the checkout service.
#  * CloudWatch Synthetics canary that walks a whole CUJ (not just GET /)
#  * Anomaly-detection alarm (statistical baseline instead of a static threshold)
#  * Log metric filter that turns structured logs into an SLI
#  * X-Ray group to slice traces by CUJ

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws     = { source = "hashicorp/aws", version = ">= 5.40" }
    archive = { source = "hashicorp/archive", version = ">= 2.4" }
  }
}

provider "aws" {
  region = var.region
}

data "aws_caller_identity" "me" {}

# ---------- Synthetic CUJ probe (ch. 8 case study: probe EVERY journey) ----------
resource "aws_s3_bucket" "canary_artifacts" {
  bucket        = "sre-canary-artifacts-${data.aws_caller_identity.me.account_id}-${var.region}"
  force_destroy = true
}

data "archive_file" "canary" {
  type        = "zip"
  source_dir  = "${path.module}/../synthetics"
  output_path = "${path.module}/build/canary.zip"
}

resource "aws_iam_role" "canary" {
  name = "sre-cuj-canary"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy" "canary" {
  role = aws_iam_role.canary.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Effect = "Allow", Action = ["s3:PutObject", "s3:GetBucketLocation"], Resource = ["${aws_s3_bucket.canary_artifacts.arn}", "${aws_s3_bucket.canary_artifacts.arn}/*"] },
      { Effect = "Allow", Action = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"], Resource = "*" },
      { Effect = "Allow", Action = ["cloudwatch:PutMetricData"], Resource = "*", Condition = { StringEquals = { "cloudwatch:namespace" = "CloudWatchSynthetics" } } },
      { Effect = "Allow", Action = ["xray:PutTraceSegments"], Resource = "*" }
    ]
  })
}

resource "aws_synthetics_canary" "checkout_cuj" {
  name                 = "checkout-cuj"
  artifact_s3_location = "s3://${aws_s3_bucket.canary_artifacts.bucket}/checkout/"
  execution_role_arn   = aws_iam_role.canary.arn
  handler              = "cuj.handler"
  zip_file             = data.archive_file.canary.output_path
  runtime_version      = var.synthetics_runtime
  start_canary         = true

  schedule {
    expression = "rate(1 minute)"
  }

  run_config {
    timeout_in_seconds = 60
    active_tracing     = true
    environment_variables = {
      BASE_URL = var.base_url
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "cuj_probe_failing" {
  alarm_name          = "checkout-cuj-probe-failing"
  alarm_description   = "Synthetic checkout journey success < 90% over 5 min"
  namespace           = "CloudWatchSynthetics"
  metric_name         = "SuccessPercent"
  dimensions          = { CanaryName = aws_synthetics_canary.checkout_cuj.name }
  statistic           = "Average"
  period              = 300
  evaluation_periods  = 1
  threshold           = 90
  comparison_operator = "LessThanThreshold"
  treat_missing_data  = "breaching" # a silent probe is a broken probe
  alarm_actions       = var.alarm_topic_arn == "" ? [] : [var.alarm_topic_arn]
}

# ---------- Statistical baseline alerting (ch. 9 "intelligent alerting") ----------
resource "aws_cloudwatch_metric_alarm" "latency_anomaly" {
  alarm_name          = "checkout-latency-anomaly"
  alarm_description   = "p90 latency outside learned band (anomaly detection, 2 std devs)"
  comparison_operator = "GreaterThanUpperThreshold"
  evaluation_periods  = 3
  datapoints_to_alarm = 3
  threshold_metric_id = "band"
  treat_missing_data  = "notBreaching"
  alarm_actions       = var.alarm_topic_arn == "" ? [] : [var.alarm_topic_arn]

  metric_query {
    id          = "m1"
    return_data = true
    metric {
      namespace   = "SRE/Checkout"
      metric_name = "http.server.duration"
      period      = 300
      stat        = "p90"
      dimensions  = { "service.name" = "checkout", cuj = "checkout" }
    }
  }

  metric_query {
    id          = "band"
    expression  = "ANOMALY_DETECTION_BAND(m1, 2)"
    label       = "expected p90"
    return_data = true
  }
}

# ---------- Logs -> SLI ----------
resource "aws_cloudwatch_log_group" "app" {
  name              = "/sre/checkout/app"
  retention_in_days = 14 # data has a finite horizon (ch. 9 retention)
}

resource "aws_cloudwatch_log_metric_filter" "server_errors" {
  name           = "checkout-5xx"
  log_group_name = aws_cloudwatch_log_group.app.name
  pattern        = "{ $.status >= 500 }"
  metric_transformation {
    name      = "Checkout5xx"
    namespace = "SRE/CheckoutLogs"
    value     = "1"
    dimensions = {
      cuj = "$.cuj"
    }
  }
}

# ---------- Traces sliced by CUJ ----------
resource "aws_xray_group" "checkout_cuj" {
  group_name        = "checkout-cuj"
  filter_expression = "annotation.cuj = \"checkout\""
  insights_configuration {
    insights_enabled      = true
    notifications_enabled = false
  }
}
