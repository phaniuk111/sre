# AMP workspace as the remote-write target for every Prometheus (or Prometheus in agent mode) on EKS,
# plus an S3 bucket for the alternative: Thanos sidecar uploading blocks.
variable "oidc_provider_arn" { type = string }
variable "oidc_provider_url" { type = string }

resource "aws_prometheus_workspace" "main" {
  alias = "platform-metrics"
  logging_configuration {
    log_group_arn = "${aws_cloudwatch_log_group.amp.arn}:*"
  }
}

resource "aws_cloudwatch_log_group" "amp" {
  name              = "/aws/prometheus/platform-metrics"
  retention_in_days = 30
}

data "aws_iam_policy_document" "irsa" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [var.oidc_provider_arn]
    }
    condition {
      test     = "StringLike"
      variable = "${var.oidc_provider_url}:sub"
      values   = ["system:serviceaccount:monitoring:prometheus*"]
    }
  }
}

resource "aws_iam_role" "remote_write" {
  name               = "amp-remote-write"
  assume_role_policy = data.aws_iam_policy_document.irsa.json
}

resource "aws_iam_role_policy_attachment" "remote_write" {
  role       = aws_iam_role.remote_write.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonPrometheusRemoteWriteAccess"
}

# Thanos alternative: blocks in S3, cheap and long-lived
resource "aws_s3_bucket" "thanos" {
  bucket_prefix = "thanos-blocks-"
}

resource "aws_s3_bucket_lifecycle_configuration" "thanos" {
  bucket = aws_s3_bucket.thanos.id
  rule {
    id     = "infrequent-access-after-30-days"
    status = "Enabled"
    filter {}
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
  }
}

output "remote_write_url" {
  value = "${aws_prometheus_workspace.main.prometheus_endpoint}api/v1/remote_write"
}
