variable "project" {}
variable "region" {}
variable "kms_arn" {}
variable "sns_policy" {
  description = "allows a custom SNS policy to be set"
  default     = "notifications"
}
