# IAM role for a Prometheus server on EKS (IRSA) that discovers EC2 targets and remote-writes to AMP.
variable "oidc_provider_arn" { type = string }
variable "oidc_provider_url" { type = string }  # without https://
variable "namespace" {
  type    = string
  default = "monitoring"
}

data "aws_iam_policy_document" "trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [var.oidc_provider_arn]
    }
    condition {
      test     = "StringEquals"
      variable = "${var.oidc_provider_url}:sub"
      values   = ["system:serviceaccount:${var.namespace}:prometheus"]
    }
  }
}

resource "aws_iam_role" "prometheus" {
  name               = "prometheus-ec2-sd"
  assume_role_policy = data.aws_iam_policy_document.trust.json
}

data "aws_iam_policy_document" "sd" {
  statement {
    sid       = "Ec2ServiceDiscovery"
    actions   = ["ec2:DescribeInstances", "ec2:DescribeAvailabilityZones"]
    resources = ["*"]
  }
  statement {
    sid       = "RemoteWrite"
    actions   = ["aps:RemoteWrite"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "sd" {
  role   = aws_iam_role.prometheus.id
  policy = data.aws_iam_policy_document.sd.json
}

output "role_arn" { value = aws_iam_role.prometheus.arn }
