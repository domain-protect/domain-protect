variable "project" {}
variable "region" {}
variable "kms_arn" {}
variable "sns_policy" {
  description = "allows a custom SNS policy to be set"
  default     = "notifications"
}

variable "dead_letter_queue" {
  description = "set SNS topic to be a dead letter queue"
  default     = false
}

variable "env" {
  type = string
}
