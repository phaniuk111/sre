# Data resilience on AWS (book ch. 16 + ch. 17 "Data Resilience").
#  * Classify data into tiers via tags -> each tier has RPO / RTO / RWO
#  * AWS Backup plans per tier, cross-Region copy (region-loss scenario)
#  * Vault Lock (compliance mode): writers to live data cannot delete backups
#    (operator error / malicious action / ransomware scenario)
#  * Restore TESTING plan: untested backups are hopes, not backups
#  * Live-data guards: DynamoDB PITR + deletion protection, S3 versioning +
#    Object Lock (staged deletion with non-bypassable grace period)

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

provider "aws" {
  alias  = "dr"
  region = var.dr_region
}

locals {
  tiers = {
    # RPO drives schedule; RWO drives retention; RTO is validated by restore tests
    tier0 = { schedule = "cron(0 * * * ? *)", retain_days = 35, copy_days = 35, continuous = true }  # RPO 1h (PITR ~5m), RWO 35d
    tier1 = { schedule = "cron(0 3 * * ? *)", retain_days = 30, copy_days = 30, continuous = false } # RPO 24h, RWO 30d
    tier2 = { schedule = "cron(0 3 ? * SUN *)", retain_days = 90, copy_days = 0, continuous = false } # weekly, derived data
  }
}

resource "aws_kms_key" "backup" {
  description         = "Backup vault key"
  enable_key_rotation = true
}

resource "aws_backup_vault" "primary" {
  name        = "sre-primary"
  kms_key_arn = aws_kms_key.backup.arn
}

resource "aws_backup_vault_lock_configuration" "primary" {
  backup_vault_name   = aws_backup_vault.primary.name
  min_retention_days  = 7
  max_retention_days  = 400
  changeable_for_days = 3 # after 3 days the lock becomes immutable (compliance mode)
}

resource "aws_kms_key" "backup_dr" {
  provider            = aws.dr
  description         = "DR backup vault key"
  enable_key_rotation = true
}

resource "aws_backup_vault" "dr" {
  provider    = aws.dr
  name        = "sre-dr"
  kms_key_arn = aws_kms_key.backup_dr.arn
}

resource "aws_backup_plan" "tiered" {
  for_each = local.tiers
  name     = "sre-${each.key}"

  rule {
    rule_name                = "${each.key}-scheduled"
    target_vault_name        = aws_backup_vault.primary.name
    schedule                 = each.value.schedule
    start_window             = 60
    completion_window        = 180
    enable_continuous_backup = each.value.continuous # PITR for supported services

    lifecycle {
      delete_after = each.value.retain_days
    }

    dynamic "copy_action" {
      for_each = each.value.copy_days > 0 ? [1] : []
      content {
        destination_vault_arn = aws_backup_vault.dr.arn # 3-2-1: off-site copy in another Region
        lifecycle {
          delete_after = each.value.copy_days
        }
      }
    }
  }
}

resource "aws_iam_role" "backup" {
  name = "sre-aws-backup"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "backup.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy_attachment" "backup" {
  role       = aws_iam_role.backup.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"
}

resource "aws_iam_role_policy_attachment" "restore" {
  role       = aws_iam_role.backup.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores"
}

# Tag-based selection: the backup plan follows the data classification, so NEW
# data sources are covered automatically (the book's "one-off sweep" failure mode).
resource "aws_backup_selection" "tiered" {
  for_each     = local.tiers
  name         = "select-${each.key}"
  plan_id      = aws_backup_plan.tiered[each.key].id
  iam_role_arn = aws_iam_role.backup.arn
  resources    = ["*"]

  condition {
    string_equals {
      key   = "aws:ResourceTag/data-tier"
      value = each.key
    }
  }
}

# Restore testing: AWS Backup restores the latest recovery point on a schedule,
# measures the duration (your real RTO), and deletes the restored copy.
resource "aws_backup_restore_testing_plan" "weekly" {
  name                         = "sre_weekly_restore_test"
  schedule_expression          = "cron(0 5 ? * MON *)"
  start_window_hours           = 2
  recovery_point_selection {
    algorithm             = "LATEST_WITHIN_WINDOW"
    include_vaults        = ["*"]
    recovery_point_types  = ["SNAPSHOT"]
    selection_window_days = 7
  }
}

resource "aws_backup_restore_testing_selection" "tier0_dynamodb" {
  name                      = "tier0_dynamodb"
  restore_testing_plan_name = aws_backup_restore_testing_plan.weekly.name
  protected_resource_type   = "DynamoDB"
  iam_role_arn              = aws_iam_role.backup.arn
  protected_resource_conditions {
    string_equals {
      key   = "aws:ResourceTag/data-tier"
      value = "tier0"
    }
  }
  validation_window_hours = 2
}

# ---------- Live data guards ----------
resource "aws_dynamodb_table" "orders" {
  name                        = "orders"
  billing_mode                = "PAY_PER_REQUEST"
  hash_key                    = "order_id"
  deletion_protection_enabled = true

  attribute {
    name = "order_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true # protects against BAD WRITES from apps; replication alone would copy the corruption
  }

  tags = { "data-tier" = "tier0", classification = "original", pii = "true" }
}

resource "aws_s3_bucket" "documents" {
  bucket_prefix       = "sre-documents-"
  object_lock_enabled = true
  tags                = { "data-tier" = "tier1", classification = "original" }
}

resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id
  versioning_configuration {
    status = "Enabled" # delete = soft delete (delete marker) by default
  }
}

resource "aws_s3_bucket_object_lock_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id
  rule {
    default_retention {
      mode = "GOVERNANCE" # grace period; only a separate, guarded role can bypass
      days = 14
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id
  rule {
    id     = "expire-noncurrent"
    status = "Enabled"
    filter {}
    noncurrent_version_expiration {
      noncurrent_days = 30 # RWO for deleted/overwritten objects; balance with data-deletion law
    }
  }
}
