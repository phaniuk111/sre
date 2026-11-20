# Progressive rollout of BOTH code and configuration with automatic rollback.
#   Code:   Lambda version -> alias "live" -> CodeDeploy canary 10% for 5 min -> 100%
#           rollback automatically if the canary alarm fires.
#   Config: AppConfig feature flag deployed gradually (linear 20%/min, 10 min bake)
#           with the same alarm as a rollback trigger.
# Book: ch. 14 (canaries, VOIS config), ch. 17 (progressive rollout, change
# supervision, change concurrency, feature flags, safe mitigations).

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

data "archive_file" "fn" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/build/fn.zip"
}

resource "aws_iam_role" "fn" {
  name = "checkout-fn"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy_attachment" "logs" {
  role       = aws_iam_role.fn.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "appconfig" {
  role = aws_iam_role.fn.id
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = ["appconfig:StartConfigurationSession", "appconfig:GetLatestConfiguration"], Resource = "*" }]
  })
}

resource "aws_lambda_function" "checkout" {
  function_name    = "checkout"
  role             = aws_iam_role.fn.arn
  runtime          = "python3.12"
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.fn.output_path
  source_code_hash = data.archive_file.fn.output_base64sha256
  publish          = true # every change creates an immutable version (Versioned)
  layers           = [var.appconfig_extension_layer_arn]
  timeout          = 5
}

resource "aws_lambda_alias" "live" {
  name             = "live"
  function_name    = aws_lambda_function.checkout.function_name
  function_version = aws_lambda_function.checkout.version
  # CodeDeploy owns traffic shifting after the first apply
  lifecycle {
    ignore_changes = [function_version, routing_config]
  }
}

# Canary health: errors on the alias. (For per-version comparison use
# canary_analysis.py in a CodeDeploy hook; CloudWatch dims include ExecutedVersion.)
resource "aws_cloudwatch_metric_alarm" "canary_errors" {
  alarm_name          = "checkout-canary-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  threshold           = 0.01
  treat_missing_data  = "notBreaching"

  metric_query {
    id          = "rate"
    expression  = "IF(inv > 0, err / inv, 0)"
    return_data = true
  }
  metric_query {
    id = "err"
    metric {
      namespace   = "AWS/Lambda"
      metric_name = "Errors"
      period      = 60
      stat        = "Sum"
      dimensions  = { FunctionName = aws_lambda_function.checkout.function_name, Resource = "${aws_lambda_function.checkout.function_name}:live" }
    }
  }
  metric_query {
    id = "inv"
    metric {
      namespace   = "AWS/Lambda"
      metric_name = "Invocations"
      period      = 60
      stat        = "Sum"
      dimensions  = { FunctionName = aws_lambda_function.checkout.function_name, Resource = "${aws_lambda_function.checkout.function_name}:live" }
    }
  }
}

resource "aws_codedeploy_app" "checkout" {
  name             = "checkout"
  compute_platform = "Lambda"
}

resource "aws_iam_role" "codedeploy" {
  name = "checkout-codedeploy"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "codedeploy.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy_attachment" "codedeploy" {
  role       = aws_iam_role.codedeploy.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRoleForLambda"
}

resource "aws_codedeploy_deployment_group" "checkout" {
  app_name               = aws_codedeploy_app.checkout.name
  deployment_group_name  = "checkout-live"
  service_role_arn       = aws_iam_role.codedeploy.arn
  deployment_config_name = "CodeDeployDefault.LambdaCanary10Percent5Minutes"

  deployment_style {
    deployment_type   = "BLUE_GREEN"
    deployment_option = "WITH_TRAFFIC_CONTROL"
  }

  alarm_configuration {
    enabled = true
    alarms  = [aws_cloudwatch_metric_alarm.canary_errors.alarm_name]
  }

  auto_rollback_configuration {
    enabled = true
    events  = ["DEPLOYMENT_FAILURE", "DEPLOYMENT_STOP_ON_ALARM"]
  }
}

# ---------------- Configuration as a separately rolled-out change ----------------
resource "aws_appconfig_application" "checkout" {
  name = "checkout"
}

resource "aws_appconfig_environment" "prod" {
  name           = "prod"
  application_id = aws_appconfig_application.checkout.id
  monitor {
    alarm_arn      = aws_cloudwatch_metric_alarm.canary_errors.arn
    alarm_role_arn = aws_iam_role.appconfig_monitor.arn
  }
}

resource "aws_iam_role" "appconfig_monitor" {
  name = "checkout-appconfig-monitor"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "appconfig.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy" "appconfig_monitor" {
  role = aws_iam_role.appconfig_monitor.id
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = ["cloudwatch:DescribeAlarms"], Resource = "*" }]
  })
}

resource "aws_appconfig_configuration_profile" "flags" {
  application_id = aws_appconfig_application.checkout.id
  name           = "flags"
  location_uri   = "hosted"
  type           = "AWS.AppConfig.FeatureFlags"
}

resource "aws_appconfig_hosted_configuration_version" "flags" {
  application_id           = aws_appconfig_application.checkout.id
  configuration_profile_id = aws_appconfig_configuration_profile.flags.configuration_profile_id
  content_type             = "application/json"
  content = jsonencode({
    version = "1"
    flags   = { recommendations = { name = "recommendations" } }
    values  = { recommendations = { enabled = var.recommendations_enabled } }
  })
}

resource "aws_appconfig_deployment_strategy" "gradual" {
  name                           = "linear-20pct-per-minute-10min-bake"
  deployment_duration_in_minutes = 5
  growth_factor                  = 20
  growth_type                    = "LINEAR"
  final_bake_time_in_minutes     = 10
  replicate_to                   = "NONE"
}

resource "aws_appconfig_deployment" "flags" {
  application_id           = aws_appconfig_application.checkout.id
  environment_id           = aws_appconfig_environment.prod.environment_id
  configuration_profile_id = aws_appconfig_configuration_profile.flags.configuration_profile_id
  configuration_version    = aws_appconfig_hosted_configuration_version.flags.version_number
  deployment_strategy_id   = aws_appconfig_deployment_strategy.gradual.id
  description              = "Flag change rolled out separately from code (change concurrency = 1)"
}
