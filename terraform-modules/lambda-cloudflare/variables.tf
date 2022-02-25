variable "project" {}
variable "cf_api_key" {}
variable "lambda_role_arn" {}
variable "kms_arn" {}
variable "lambdas" {}
variable "runtime" {}
variable "memory_size" {}
variable "security_audit_role_name" {}
variable "external_id" {}
variable "org_primary_account" {}
variable "sns_topic_arn" {}

variable "state_machine_arn" {
  default = ""
}

variable "timeout" {
  description = "Amount of time your Lambda Function has to run in seconds"
  default     = 900
}
