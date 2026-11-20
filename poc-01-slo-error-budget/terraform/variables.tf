variable "region" {
  type    = string
  default = "eu-west-2"
}

variable "service_name" {
  type        = string
  description = "Short service name used in alarm names"
  default     = "checkout"
}

variable "alb_arn_suffix" {
  type        = string
  description = "The ALB ARN suffix, e.g. app/my-alb/0123456789abcdef (aws_lb.this.arn_suffix)"
}

variable "slo_target" {
  type        = number
  description = "Availability SLO as a ratio, e.g. 0.999"
  default     = 0.999

  validation {
    condition     = var.slo_target > 0 && var.slo_target < 1
    error_message = "SLO must be between 0 and 1 (never 100%)."
  }
}

variable "latency_slo_percentile" {
  type    = string
  default = "p99"
}

variable "latency_threshold_seconds" {
  type    = number
  default = 0.3
}

variable "runbook_url" {
  type    = string
  default = "https://github.com/phaniuk111/sre/blob/main/poc-03-incident-management/playbooks/slo-burn.md"
}
