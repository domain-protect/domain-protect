variable "project" {
  description = "abbreviation for the project, forms first part of resource names"
  default     = "domain-protect"
}

variable "region" {
  description = "AWS region to deploy Lambda functions"
  default     = "eu-west-1"
}

variable "org_primary_account" {
  description = "The AWS account number of the organization primary account"
  default     = ""
}

variable "security_audit_role_name" {
  description = "security audit role name which needs to be the same in all AWS accounts"
  default     = "domain-protect-audit"
}

variable "external_id" {
  description = "external ID for security audit role to be defined in tvars file. Leave empty if not configured"
  default     = ""
}

variable "schedule" {
  description = "schedule for running domain-protect, e.g. 24 hours, 60 minutes"
  default     = "24 hours"
}

variable "lambdas" {
  description = "list of names of Lambda files in the lambda/code folder"
  default     = ["alias-eb", "alias-s3", "cname-eb", "cname-s3", "ns"]
}

variable "runtime" {
  description = "Lambda language runtime"
  default     = "python3.8"
}

variable "slack_channels" {
  description = "List of Slack Channel name - enter in tfvars file"
  default     = []
}

variable "slack_channels_dev" {
  description = "List of Slack Channel names to use for testing purposes with dev environment - enter in tfvars file"
  default     = []
}

variable "slack_webhook_urls" {
  description = "List of Slack webhook URLs, in the same order as Slack channel names - enter in tfvars file"
  default     = []
}

variable "slack_emoji" {
  description = "Slack emoji"
  default     = ":warning:"
}

variable "slack_username" {
  description = "Slack username appearing in the from field in the Slack message"
  default     = "Domain Protect"
}
