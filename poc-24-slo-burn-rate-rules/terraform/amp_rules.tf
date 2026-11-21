# Load the generated SLO rules into an Amazon Managed Service for Prometheus workspace, and route
# the page and ticket alerts through the AMP alert manager to SNS.
variable "workspace_id" { type = string }
variable "page_topic_arn" { type = string }
variable "ticket_topic_arn" { type = string }

resource "aws_prometheus_rule_group_namespace" "slo" {
  name         = "slo-checkout"
  workspace_id = var.workspace_id
  data         = file("${path.module}/../generated/slo-rules.yml")
}

resource "aws_prometheus_alert_manager_definition" "this" {
  workspace_id = var.workspace_id
  definition   = <<-EOT
    alertmanager_config: |
      route:
        receiver: ticket
        group_by: [alertname, sloth_service, sloth_slo]
        repeat_interval: 12h
        routes:
          - receiver: page
            matchers: [sloth_severity="page"]
            repeat_interval: 1h
      receivers:
        - name: page
          sns_configs:
            - topic_arn: ${var.page_topic_arn}
              sigv4:
                region: eu-west-2
        - name: ticket
          sns_configs:
            - topic_arn: ${var.ticket_topic_arn}
              sigv4:
                region: eu-west-2
  EOT
}
