variable "region" {
  type    = string
  default = "eu-west-2"
}

variable "base_url" {
  type        = string
  description = "Public URL of the checkout service the canary should exercise"
  default     = "https://example.com"
}

variable "synthetics_runtime" {
  type        = string
  description = "CloudWatch Synthetics runtime; check the console for the newest supported value"
  default     = "syn-nodejs-puppeteer-9.1"
}

variable "alarm_topic_arn" {
  type        = string
  description = "SNS topic for notifications (e.g. output of POC 01)"
  default     = ""
}
