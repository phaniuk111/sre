# Incident response wiring on AWS, modelled on IMAG (ch. 10):
#   SLO burn alarm (POC 01) --> AWS Systems Manager Incident Manager response plan
#   --> engage on-call (contacts/escalation) --> chat channel --> runbook (SSM Automation)
#   --> timeline captured automatically --> post-incident analysis template.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.40" }
  }
}

provider "aws" {
  region = var.region
}

resource "aws_ssmincidents_replication_set" "this" {
  region {
    name = var.region
  }
  region {
    name = var.secondary_region # Incident tooling must survive a regional outage (ch. 17 emergency mode)
  }
}

resource "aws_ssmcontacts_contact" "primary_oncall" {
  alias        = "checkout-primary"
  display_name = "Checkout primary on-call"
  type         = "PERSONAL"
  depends_on   = [aws_ssmincidents_replication_set.this]
}

resource "aws_ssmcontacts_contact_channel" "primary_sms" {
  contact_id = aws_ssmcontacts_contact.primary_oncall.arn
  name       = "primary-sms"
  type       = "SMS"
  delivery_address {
    simple_address = var.oncall_phone
  }
}

resource "aws_ssmcontacts_contact" "secondary_oncall" {
  alias        = "checkout-secondary"
  display_name = "Checkout secondary on-call"
  type         = "PERSONAL"
  depends_on   = [aws_ssmincidents_replication_set.this]
}

resource "aws_ssmcontacts_contact" "escalation" {
  alias        = "checkout-escalation"
  display_name = "Checkout escalation plan"
  type         = "ESCALATION"
  depends_on   = [aws_ssmincidents_replication_set.this]
}

resource "aws_ssmcontacts_plan" "escalation" {
  contact_id = aws_ssmcontacts_contact.escalation.arn

  stage {
    duration_in_minutes = 5 # 5-minute response expectation for this service
    target {
      contact_target_info {
        is_essential = true
        contact_id   = aws_ssmcontacts_contact.primary_oncall.arn
      }
    }
  }

  stage {
    duration_in_minutes = 10
    target {
      contact_target_info {
        is_essential = true
        contact_id   = aws_ssmcontacts_contact.secondary_oncall.arn
      }
    }
  }
}

resource "aws_ssmincidents_response_plan" "slo_burn" {
  name         = "checkout-slo-fast-burn"
  display_name = "Checkout: SLO fast burn"

  incident_template {
    title         = "Checkout error budget burning fast"
    impact        = 2 # 1=critical ... 5=no impact; triage refines this
    summary       = "Fast-burn SLO alert. IC: assign roles (IC / Comms / Ops). Mitigate first: roll back, drain, upsize, degrade, block."
    dedupe_string = "checkout-slo-fast-burn"
    incident_tags = { service = "checkout", source = "slo" }
  }

  engagements = [aws_ssmcontacts_contact.escalation.arn]

  action {
    ssm_automation {
      document_name    = var.mitigation_document_name
      role_arn         = var.automation_role_arn
      document_version = "$DEFAULT"
      target_account   = "RESPONSE_PLAN_OWNER_ACCOUNT"
      parameter {
        name   = "ServiceName"
        values = ["checkout"]
      }
      dynamic_parameters = {
        IncidentRecordArn = "INCIDENT_RECORD_ARN"
      }
    }
  }

  tags = { book_chapter = "10" }

  depends_on = [aws_ssmincidents_replication_set.this]
}

# Point the composite alarm from POC 01 straight at the response plan.
# (CloudWatch alarm actions accept an Incident Manager response-plan ARN.)
output "response_plan_arn" {
  value       = aws_ssmincidents_response_plan.slo_burn.arn
  description = "Add this ARN to alarm_actions of the page-severity composite alarms"
}
