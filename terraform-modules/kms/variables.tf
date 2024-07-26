variable "project" {}
variable "region" {}

variable "kms_policy" {
  description = "KMS policy to use"
  default     = "default"
}

variable "env" {
  type = string
}
