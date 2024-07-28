variable "project" {}
variable "security_audit_role_name" {}
variable "external_id" {}
variable "org_primary_account" {}
variable "lambda_role_arn" {}
variable "kms_arn" {}
variable "runtime" {}
variable "platform" {}
variable "memory_size" {}
variable "sns_topic_arn" {}
variable "dlq_sns_topic_arn" {}
variable "state_machine_arn" {}
variable "lambdas" {}

variable "timeout" {
  description = "Amount of time your Lambda Function has to run in seconds"
  default     = 900
}

variable "environment" {
  type = string
}
