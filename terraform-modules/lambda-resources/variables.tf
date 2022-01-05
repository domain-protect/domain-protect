variable "project" {}
variable "lambda_role_arn" {}
variable "kms_arn" {}
variable "runtime" {}
variable "memory_size" {}
variable "sns_topic_arn" {}

variable "lambdas" {
  description = "List of Lambda functions"
  default     = ["resources"]
}

variable "timeout" {
  description = "Amount of time your Lambda Function has to run in seconds"
  default     = 900
}