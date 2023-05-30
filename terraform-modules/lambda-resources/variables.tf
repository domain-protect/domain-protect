variable "project" {}
variable "lambda_role_arn" {}
variable "kms_arn" {}
variable "runtime" {}
variable "memory_size" {}
variable "sns_topic_arn" {}
variable "dlq_sns_topic_arn" {}
variable "lambdas" {}

variable "state_machine_arn" {
  default = ""
}

variable "timeout" {
  description = "Amount of time your Lambda Function has to run in seconds"
  default     = 900
}
