# Risk profiles as CodeDeploy deployment configurations for Lambda.
# The golden-path pipeline picks the configuration from the service's tier, so a
# team never chooses how careful to be: the platform does.
#   tier 1  canary 10% for 30 minutes, then the rest   (plus alarms -> automatic rollback)
#   tier 2  linear 25% every 5 minutes
#   tier 3  all at once
# Pair each deployment group with CloudWatch alarms on the service's SLO burn
# rate (POC 01) and auto_rollback_configuration, as in POC 05.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.40" }
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  type    = string
  default = "eu-west-1"
}

resource "aws_codedeploy_deployment_config" "tier1" {
  deployment_config_name = "platform-tier1-canary10-30min"
  compute_platform       = "Lambda"

  traffic_routing_config {
    type = "TimeBasedCanary"

    time_based_canary {
      interval   = 30
      percentage = 10
    }
  }
}

resource "aws_codedeploy_deployment_config" "tier2" {
  deployment_config_name = "platform-tier2-linear25-5min"
  compute_platform       = "Lambda"

  traffic_routing_config {
    type = "TimeBasedLinear"

    time_based_linear {
      interval   = 5
      percentage = 25
    }
  }
}

locals {
  config_by_tier = {
    "1" = aws_codedeploy_deployment_config.tier1.deployment_config_name
    "2" = aws_codedeploy_deployment_config.tier2.deployment_config_name
    "3" = "CodeDeployDefault.LambdaAllAtOnce"
  }
}

output "deployment_config_by_tier" {
  value = local.config_by_tier
}
