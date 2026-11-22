# The same rules, on AWS: an Amazon Managed Service for Prometheus workspace that evaluates the
# journey SLO and burn-rate alerts, and routes pages and tickets through SNS.
# On EKS, measure the journey where every attempt passes: the ingress controller or gateway
# (scraped by the ADOT collector or AMP's managed collector and remote-written here). An ALB's
# CloudWatch metrics have no per-route detail, so they can't give you a per-journey SLI by themselves.
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.0" }
  }
}

variable "region" {
  type    = string
  default = "eu-west-2"
}

provider "aws" {
  region = var.region
}

resource "aws_prometheus_workspace" "lab" {
  alias = "checkout-journey-slo"
}

resource "aws_prometheus_rule_group_namespace" "checkout_slo" {
  name         = "checkout-journey-slo"
  workspace_id = aws_prometheus_workspace.lab.id
  data         = file("${path.module}/../rules/checkout-slo.yml")
}

resource "aws_prometheus_rule_group_namespace" "internal_slos" {
  name         = "checkout-internal-slos"
  workspace_id = aws_prometheus_workspace.lab.id
  data         = file("${path.module}/../solutions/internal-slos.yml")
}

resource "aws_sns_topic" "page" {
  name = "checkout-slo-page"
}

resource "aws_sns_topic" "ticket" {
  name = "checkout-slo-ticket"
}

resource "aws_prometheus_alert_manager_definition" "lab" {
  workspace_id = aws_prometheus_workspace.lab.id
  definition   = <<-EOT
    alertmanager_config: |
      route:
        receiver: ticket
        group_by: [alertname, journey]
        repeat_interval: 12h
        routes:
          - receiver: page
            matchers: [severity="page"]
            repeat_interval: 1h
      receivers:
        - name: page
          sns_configs:
            - topic_arn: ${aws_sns_topic.page.arn}
              sigv4:
                region: ${var.region}
        - name: ticket
          sns_configs:
            - topic_arn: ${aws_sns_topic.ticket.arn}
              sigv4:
                region: ${var.region}
  EOT
}

output "remote_write_url" {
  value = "${aws_prometheus_workspace.lab.prometheus_endpoint}api/v1/remote_write"
}
