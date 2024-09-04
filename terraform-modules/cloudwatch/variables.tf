variable "project" {}
variable "lambda_function_arns" {}
variable "lambda_function_names" {}
variable "lambda_function_alias_names" {}
variable "schedule" {}
variable "takeover" {}
variable "update_lambdas" {}
variable "update_schedule" {}

variable "environment" {
  type = string
}
