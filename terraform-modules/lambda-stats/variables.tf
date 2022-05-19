variable "project" {}
variable "lambda_role_arn" {}
variable "kms_arn" {}
variable "runtime" {}
variable "memory_size" {}
variable "dlq_sns_topic_arn" {}
variable "sns_topic_arn" {}
variable "schedule_experession" {}
variable "org_primary_account" {}
variable "security_audit_role_name" {}
variable "external_id" {}

variable "timeout" {
  description = "Amount of time your Lambda Function has to run in seconds"
  default     = 900
}
