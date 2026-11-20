variable "region" {
  type    = string
  default = "eu-west-2"
}

variable "appconfig_extension_layer_arn" {
  type        = string
  description = "Region-specific ARN of the AWS AppConfig Lambda extension layer (see AWS docs for the current ARN)"
}

variable "recommendations_enabled" {
  type    = bool
  default = false
}
