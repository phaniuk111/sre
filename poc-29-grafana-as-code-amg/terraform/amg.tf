# Amazon Managed Grafana workspace wired to AMP, CloudWatch and X-Ray, with dashboards, folders,
# permissions and a Grafana-managed alert rule group managed through the grafana provider.
terraform {
  required_providers {
    aws     = { source = "hashicorp/aws" }
    grafana = { source = "grafana/grafana" }
  }
}

variable "amp_workspace_id" { type = string }
variable "region" {
  type    = string
  default = "eu-west-2"
}
variable "checkout_team_id" { type = string }

data "aws_iam_policy_document" "grafana_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["grafana.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "grafana" {
  name               = "amg-workspace"
  assume_role_policy = data.aws_iam_policy_document.grafana_trust.json
}

resource "aws_iam_role_policy_attachment" "amp" {
  role       = aws_iam_role.grafana.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonPrometheusQueryAccess"
}

resource "aws_grafana_workspace" "main" {
  name                     = "platform"
  account_access_type      = "CURRENT_ACCOUNT"
  authentication_providers = ["AWS_SSO"]
  permission_type          = "SERVICE_MANAGED"
  role_arn                 = aws_iam_role.grafana.arn
  data_sources             = ["PROMETHEUS", "CLOUDWATCH", "XRAY"]
}

# A short-lived key for Terraform itself; CI uses a service account token instead.
resource "aws_grafana_workspace_api_key" "terraform" {
  key_name        = "terraform"
  key_role        = "ADMIN"
  seconds_to_live = 3600
  workspace_id    = aws_grafana_workspace.main.id
}

provider "grafana" {
  url  = "https://${aws_grafana_workspace.main.endpoint}"
  auth = aws_grafana_workspace_api_key.terraform.key
}

resource "grafana_data_source" "amp" {
  type = "prometheus"
  name = "AMP"
  uid  = "amp"
  url  = "https://aps-workspaces.${var.region}.amazonaws.com/workspaces/${var.amp_workspace_id}"
  json_data_encoded = jsonencode({
    httpMethod    = "POST"
    sigV4Auth     = true
    sigV4AuthType = "ec2_iam_role"
    sigV4Region   = var.region
  })
}

resource "grafana_folder" "checkout" {
  title = "Checkout"
}

# Teams own their folder: edit rights inside it, view rights everywhere else.
resource "grafana_folder_permission" "checkout" {
  folder_uid = grafana_folder.checkout.uid
  permissions {
    team_id    = var.checkout_team_id
    permission = "Edit"
  }
  permissions {
    role       = "Viewer"
    permission = "View"
  }
}

resource "grafana_dashboard" "golden_signals" {
  for_each    = fileset("${path.module}/../dashboards", "*.json")
  folder      = grafana_folder.checkout.uid
  config_json = file("${path.module}/../dashboards/${each.value}")
  overwrite   = true
}

resource "grafana_rule_group" "checkout" {
  name             = "checkout-slo"
  folder_uid       = grafana_folder.checkout.uid
  interval_seconds = 60
  rule {
    name      = "CheckoutHighErrorRate"
    condition = "C"
    for       = "5m"
    labels    = { severity = "critical", team = "checkout" }
    annotations = {
      summary     = "Checkout error rate is above 3 percent."
      runbook_url = "https://runbooks.example.com/checkout"
    }
    data {
      ref_id         = "A"
      datasource_uid = grafana_data_source.amp.uid
      relative_time_range {
        from = 600
        to   = 0
      }
      model = jsonencode({ expr = "sum(rate(http_server_requests_total{service=\"checkout\",code=~\"5..\"}[10m])) / sum(rate(http_server_requests_total{service=\"checkout\"}[10m])) * 100", refId = "A" })
    }
    data {
      ref_id         = "C"
      datasource_uid = "__expr__"
      relative_time_range {
        from = 0
        to   = 0
      }
      model = jsonencode({ type = "threshold", expression = "A", conditions = [{ evaluator = { type = "gt", params = [3] } }], refId = "C" })
    }
  }
}

output "grafana_url" { value = "https://${aws_grafana_workspace.main.endpoint}" }
