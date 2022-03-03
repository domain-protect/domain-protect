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
variable "production_workspace" {}
variable "bugcrowd" {}
variable "bugcrowd_api_key" {}
variable "bugcrowd_email" {}
variable "bugcrowd_state" {}

variable "timeout" {
  description = "Amount of time your Lambda Function has to run in seconds"
  default     = 900
}
