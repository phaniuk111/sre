# Multi-window, multi-burn-rate SLO alerting for an Application Load Balancer.
#
# SLI (availability) = 1 - (target 5xx + ELB 5xx) / RequestCount
# Each rule = composite alarm of (long window AND short window) so it pages when
# the problem is significant AND still happening, and auto-resolves fast.
#
# CloudWatch limits: alarm period <= 1 day, so the 3-day slow-burn window from
# the book is approximated with the Workbook's 1-day/2-hour ticket rule. If you
# need the exact 3d window, use CloudWatch Application Signals SLOs (native SLO
# objects with burn-rate alarms) or evaluate from a scheduled Lambda.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.40"
    }
  }
}

provider "aws" {
  region = var.region
}

locals {
  error_budget = 1 - var.slo_target

  # name => {long, short (seconds), burn rate, severity}
  rules = {
    page_fast   = { long = 3600, short = 300, burn = 14.4, severity = "page" }   # 2% of 30d budget in 1h
    page_medium = { long = 21600, short = 1800, burn = 6, severity = "page" }    # 5% in 6h
    ticket_slow = { long = 86400, short = 7200, burn = 3, severity = "ticket" }  # 10% in 1d
  }

  windows = merge([
    for name, r in local.rules : {
      "${name}_long"  = { rule = name, period = r.long, burn = r.burn }
      "${name}_short" = { rule = name, period = r.short, burn = r.burn }
    }
  ]...)
}

resource "aws_sns_topic" "page" {
  name = "${var.service_name}-slo-page"
}

resource "aws_sns_topic" "ticket" {
  name = "${var.service_name}-slo-ticket"
}

resource "aws_cloudwatch_metric_alarm" "burn_window" {
  for_each = local.windows

  alarm_name          = "${var.service_name}-${each.key}"
  alarm_description   = "Error ratio over ${each.value.period}s exceeds burn rate ${each.value.burn} for SLO ${var.slo_target}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  threshold           = each.value.burn * local.error_budget
  treat_missing_data  = "notBreaching"

  metric_query {
    id          = "error_ratio"
    expression  = "IF(requests > 0, (target5xx + elb5xx) / requests, 0)"
    label       = "error ratio"
    return_data = true
  }

  metric_query {
    id = "requests"
    metric {
      namespace   = "AWS/ApplicationELB"
      metric_name = "RequestCount"
      period      = each.value.period
      stat        = "Sum"
      dimensions  = { LoadBalancer = var.alb_arn_suffix }
    }
  }

  metric_query {
    id = "target5xx"
    metric {
      namespace   = "AWS/ApplicationELB"
      metric_name = "HTTPCode_Target_5XX_Count"
      period      = each.value.period
      stat        = "Sum"
      dimensions  = { LoadBalancer = var.alb_arn_suffix }
    }
  }

  metric_query {
    id = "elb5xx"
    metric {
      namespace   = "AWS/ApplicationELB"
      metric_name = "HTTPCode_ELB_5XX_Count"
      period      = each.value.period
      stat        = "Sum"
      dimensions  = { LoadBalancer = var.alb_arn_suffix }
    }
  }
}

# Composite = long AND short. This is what actually notifies humans.
resource "aws_cloudwatch_composite_alarm" "burn_rule" {
  for_each = local.rules

  alarm_name        = "${var.service_name}-slo-${each.key}"
  alarm_description = "SLO ${var.slo_target}: burn rate > ${each.value.burn}x on both ${each.value.long}s and ${each.value.short}s windows. Runbook: ${var.runbook_url}"
  alarm_rule = join(" AND ", [
    "ALARM(\"${aws_cloudwatch_metric_alarm.burn_window["${each.key}_long"].alarm_name}\")",
    "ALARM(\"${aws_cloudwatch_metric_alarm.burn_window["${each.key}_short"].alarm_name}\")",
  ])

  alarm_actions = [each.value.severity == "page" ? aws_sns_topic.page.arn : aws_sns_topic.ticket.arn]
  ok_actions    = [each.value.severity == "page" ? aws_sns_topic.page.arn : aws_sns_topic.ticket.arn]
}

# Latency SLI: % of requests faster than threshold. ALB exposes percentiles, so
# we alert when p(SLO) latency exceeds the threshold - equivalent to "fewer than
# SLO% of requests were faster than X" for a single window.
resource "aws_cloudwatch_metric_alarm" "latency_slo" {
  alarm_name          = "${var.service_name}-latency-slo"
  alarm_description   = "${var.latency_slo_percentile} latency above ${var.latency_threshold_seconds}s for 3 of 5 minutes"
  namespace           = "AWS/ApplicationELB"
  metric_name         = "TargetResponseTime"
  extended_statistic  = var.latency_slo_percentile
  dimensions          = { LoadBalancer = var.alb_arn_suffix }
  period              = 60
  evaluation_periods  = 5
  datapoints_to_alarm = 3
  threshold           = var.latency_threshold_seconds
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.ticket.arn]
}

resource "aws_cloudwatch_dashboard" "slo" {
  dashboard_name = "${var.service_name}-slo"
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric", x = 0, y = 0, width = 12, height = 6
        properties = {
          title  = "Availability SLI (1h) vs SLO ${var.slo_target}"
          region = var.region
          view   = "timeSeries"
          metrics = [
            [{ expression = "100 * (1 - (t5 + e5) / req)", label = "availability %", id = "sli" }],
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", var.alb_arn_suffix, { id = "req", stat = "Sum", period = 3600, visible = false }],
            [".", "HTTPCode_Target_5XX_Count", ".", ".", { id = "t5", stat = "Sum", period = 3600, visible = false }],
            [".", "HTTPCode_ELB_5XX_Count", ".", ".", { id = "e5", stat = "Sum", period = 3600, visible = false }],
          ]
          annotations = { horizontal = [{ value = var.slo_target * 100, label = "SLO" }] }
        }
      },
      {
        type   = "metric", x = 12, y = 0, width = 12, height = 6
        properties = {
          title  = "Burn rate (1h)"
          region = var.region
          view   = "timeSeries"
          metrics = [
            [{ expression = "((t5 + e5) / req) / ${local.error_budget}", label = "burn rate", id = "br" }],
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", var.alb_arn_suffix, { id = "req", stat = "Sum", period = 3600, visible = false }],
            [".", "HTTPCode_Target_5XX_Count", ".", ".", { id = "t5", stat = "Sum", period = 3600, visible = false }],
            [".", "HTTPCode_ELB_5XX_Count", ".", ".", { id = "e5", stat = "Sum", period = 3600, visible = false }],
          ]
          annotations = { horizontal = [{ value = 14.4, label = "page" }, { value = 1, label = "sustainable" }] }
        }
      }
    ]
  })
}
