# The AWS side of the gate.
#   * AWS Signer profile + Lambda code signing config (Enforce): unsigned or
#     wrongly signed code cannot be deployed to a function that uses this config.
#   * ECR repository with immutable tags and scan-on-push, so a tag always means
#     the same digest and every image has scan findings attached.
#   * A break-glass role whose use is announced: CloudTrail records the
#     AssumeRole call, EventBridge matches it, SNS pages security.
# For containers on EKS, verify image signatures at admission with Kyverno or
# Gatekeeper; the policy logic is the same as gate.py.

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

variable "security_email" {
  type        = string
  description = "Where break-glass alerts go"
}

data "aws_caller_identity" "current" {}

resource "aws_signer_signing_profile" "prod" {
  platform_id = "AWSLambda-SHA384-ECDSA"
  name_prefix = "prod_release_"

  signature_validity_period {
    value = 12
    type  = "MONTHS"
  }
}

resource "aws_lambda_code_signing_config" "enforce" {
  description = "Only code signed by the production build profile may deploy"

  allowed_publishers {
    signing_profile_version_arns = [aws_signer_signing_profile.prod.version_arn]
  }

  policies {
    untrusted_artifact_on_deployment = "Enforce"
  }
}

resource "aws_ecr_repository" "service" {
  name                 = "orders"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_sns_topic" "break_glass" {
  name = "break-glass-alerts"
}

resource "aws_sns_topic_subscription" "security" {
  topic_arn = aws_sns_topic.break_glass.arn
  protocol  = "email"
  endpoint  = var.security_email
}

resource "aws_iam_role" "break_glass" {
  name                 = "break-glass-deployer"
  max_session_duration = 3600

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root" }
      Condition = {
        Bool = { "aws:MultiFactorAuthPresent" = "true" }
      }
    }]
  })
}

resource "aws_cloudwatch_event_rule" "break_glass_used" {
  name        = "break-glass-role-assumed"
  description = "Someone assumed the break-glass role. Page security; review afterwards."

  event_pattern = jsonencode({
    source        = ["aws.sts"]
    "detail-type" = ["AWS API Call via CloudTrail"]
    detail = {
      eventName         = ["AssumeRole"]
      requestParameters = { roleArn = [aws_iam_role.break_glass.arn] }
    }
  })
}

resource "aws_cloudwatch_event_target" "page" {
  rule = aws_cloudwatch_event_rule.break_glass_used.name
  arn  = aws_sns_topic.break_glass.arn
}

resource "aws_sns_topic_policy" "allow_events" {
  arn = aws_sns_topic.break_glass.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "events.amazonaws.com" }
      Action    = "sns:Publish"
      Resource  = aws_sns_topic.break_glass.arn
    }]
  })
}

output "code_signing_config_arn" {
  value = aws_lambda_code_signing_config.enforce.arn
}
