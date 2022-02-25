variable "project" {}

variable "lambda_arn" {
  description = "Lambda function invoked by state machine"
}

variable "role_arn" {
  description = "IAM role to be assumed by state machine"
}
