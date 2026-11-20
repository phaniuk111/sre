# Fault injection with AWS Fault Injection Service (FIS) - book ch. 14 (DiRT,
# fault injection) and ch. 17 (qualification in realistic environments).
#
# Experiments follow "workflow X is resilient to fault Y as measured by Z":
#   1. az-loss:      checkout stays within SLO when every instance in one AZ stops
#   2. dep-latency:  checkout degrades gracefully when the payments dependency
#                    gets +300ms latency
# Both have a STOP CONDITION: the SLO fast-burn alarm. If users are really hurt,
# FIS halts the experiment and rolls back.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.40" }
  }
}

provider "aws" {
  region = var.region
}

resource "aws_iam_role" "fis" {
  name = "sre-fis-experiments"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "fis.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy_attachment" "fis_ec2" {
  role       = aws_iam_role.fis.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSFaultInjectionSimulatorEC2Access"
}

resource "aws_iam_role_policy_attachment" "fis_ssm" {
  role       = aws_iam_role.fis.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSFaultInjectionSimulatorSSMAccess"
}

resource "aws_cloudwatch_log_group" "fis" {
  name              = "/sre/fis"
  retention_in_days = 30
}

resource "aws_fis_experiment_template" "az_loss" {
  description = "X=checkout CUJ, Y=loss of all instances in ${var.target_az}, Z=SLO burn alarm stays OK"
  role_arn    = aws_iam_role.fis.arn

  stop_condition {
    source = "aws:cloudwatch:alarm"
    value  = var.stop_condition_alarm_arn
  }

  target {
    name           = "checkout-in-one-az"
    resource_type  = "aws:ec2:instance"
    selection_mode = "ALL"
    resource_tag {
      key   = "service"
      value = "checkout"
    }
    filter {
      path   = "Placement.AvailabilityZone"
      values = [var.target_az]
    }
    filter {
      path   = "State.Name"
      values = ["running"]
    }
  }

  action {
    name      = "stop-az-instances"
    action_id = "aws:ec2:stop-instances"
    target {
      key   = "Instances"
      value = "checkout-in-one-az"
    }
    parameter {
      key   = "startInstancesAfterDuration"
      value = "PT10M"
    }
  }

  log_configuration {
    log_schema_version = 2
    cloudwatch_logs_configuration {
      log_group_arn = "${aws_cloudwatch_log_group.fis.arn}:*"
    }
  }

  tags = { Name = "checkout-az-loss", book = "ch14-ch17" }
}

resource "aws_fis_experiment_template" "dependency_latency" {
  description = "X=checkout, Y=+300ms to payments calls, Z=checkout p99 < 1s and recommendations degrade (not fail)"
  role_arn    = aws_iam_role.fis.arn

  stop_condition {
    source = "aws:cloudwatch:alarm"
    value  = var.stop_condition_alarm_arn
  }

  target {
    name           = "checkout-hosts"
    resource_type  = "aws:ec2:instance"
    selection_mode = "PERCENT(50)" # start small; widen once it passes
    resource_tag {
      key   = "service"
      value = "checkout"
    }
  }

  action {
    name      = "payments-latency"
    action_id = "aws:ssm:send-command"
    target {
      key   = "Instances"
      value = "checkout-hosts"
    }
    parameter {
      key   = "documentArn"
      value = "arn:aws:ssm:${var.region}::document/AWSFIS-Run-Network-Latency-Sources"
    }
    parameter {
      key   = "documentParameters"
      value = jsonencode({ DelayMilliseconds = "300", Sources = var.payments_endpoint, DurationSeconds = "300", InstallDependencies = "True" })
    }
    parameter {
      key   = "duration"
      value = "PT6M"
    }
  }

  tags = { Name = "checkout-payments-latency", book = "ch14" }
}
