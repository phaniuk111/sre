variable "region" {
  type    = string
  default = "eu-west-2"
}

variable "subnet_ids" {
  type        = list(string)
  description = "One private subnet per AZ (3 recommended)"
}

variable "availability_zones" {
  type    = list(string)
  default = ["eu-west-2a", "eu-west-2b", "eu-west-2c"]
}

variable "launch_template_id" {
  type = string
}

variable "target_group_arn" {
  type = string
}

variable "alb_resource_label" {
  type        = string
  description = "app/<alb-name>/<id>/targetgroup/<tg-name>/<id>"
}

variable "peak_qps" {
  type    = number
  default = 9000
}

variable "qps_per_instance" {
  type        = number
  description = "Measured by load test: max QPS an instance serves within latency SLO"
  default     = 100
}

variable "target_utilisation" {
  type    = number
  default = 0.7
}

variable "peak_event_start" {
  type    = string
  default = "2026-11-27T06:00:00Z"
}

variable "peak_event_end" {
  type    = string
  default = "2026-12-01T06:00:00Z"
}

variable "reserve_peak_capacity" {
  type    = bool
  default = false
}
