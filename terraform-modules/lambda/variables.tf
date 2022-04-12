variable "project" {}
variable "security_audit_role_name" {}
variable "external_id" {}
variable "org_primary_account" {}
variable "lambda_role_arn" {}
variable "kms_arn" {}
variable "lambdas" {}
variable "runtime" {}
variable "memory_size" {}
variable "sns_topic_arn" {}
variable "dlq_sns_topic_arn" {}
variable "allowed_regions" {}

variable "timeout" {
  description = "Amount of time your Lambda Function has to run in seconds"
  default     = 900
}

variable "state_machine_arn" {
  default = ""
}