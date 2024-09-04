variable "project" {}
variable "kms_arn" {}

variable "lambda_arn" {
  description = "Lambda function invoked by state machine"
}

variable "role_arn" {
  description = "IAM role to be assumed by state machine"
}

variable "retention_in_days" {
  description = "specifies the number of days you want to retain log events"
  default     = 90
}

variable "purpose" {
  description = "purpose of Step Function"
  default     = "scan"
}

variable "environment" {
  type = string
}
