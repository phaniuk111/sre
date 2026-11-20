variable "region" {
  type    = string
  default = "eu-west-2"
}

variable "target_az" {
  type    = string
  default = "eu-west-2a"
}

variable "stop_condition_alarm_arn" {
  type        = string
  description = "ARN of the SLO fast-burn alarm (POC 01). FIS stops the experiment if it goes into ALARM."
}

variable "payments_endpoint" {
  type        = string
  description = "Hostname/IP of the payments dependency to delay"
  default     = "payments.internal"
}
