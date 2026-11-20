variable "region" {
  type    = string
  default = "eu-west-2"
}

variable "dr_region" {
  type        = string
  description = "Backup copy destination. Check data-residency rules before choosing (ch. 16)."
  default     = "eu-west-1"
}
