variable "region" {
  type    = string
  default = "eu-west-2"
}

variable "secondary_region" {
  type    = string
  default = "eu-west-1"
}

variable "oncall_phone" {
  type        = string
  description = "E.164 phone number for the primary on-call (e.g. +447700900000)"
}

variable "mitigation_document_name" {
  type        = string
  description = "SSM Automation document run when the incident opens (see POC 09 generic-mitigation runbook)"
  default     = "SRE-GenericMitigation-Diagnose"
}

variable "automation_role_arn" {
  type        = string
  description = "IAM role Incident Manager assumes to start the SSM Automation"
}
