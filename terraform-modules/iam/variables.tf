variable "project" {}
variable "security_audit_role_name" {}
variable "kms_arn" {}

variable "policy" {
  description = "policy template to use"
  default     = "lambda"
}

variable "takeover" {
  description = "include managed policies to enable takeover"
  default     = false
}