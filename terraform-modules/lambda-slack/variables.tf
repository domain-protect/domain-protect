variable "project" {}
variable "lambda_role_arn" {}
variable "kms_arn" {}
variable "runtime" {}
variable "memory_size" {}
variable "sns_topic_arn" {}
variable "dlq_sns_topic_arn" {}
variable "slack_channels" {}
variable "slack_webhook_urls_secret_ids" {}
variable "slack_webhook_type" {}
variable "slack_emoji" {}
variable "slack_fix_emoji" {}
variable "slack_new_emoji" {}
variable "slack_username" {}

variable "timeout" {
  description = "Amount of time your Lambda Function has to run in seconds"
  default     = 900
}
