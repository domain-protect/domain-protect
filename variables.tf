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

variable "ip_time_limit" {
  description = "maximum time in hours since IP last detected, before considering IP as no longer belonging to organisation"
  default     = "48"
}

variable "reports_schedule" {
  description = "schedule for running reports, e.g. 24 hours. Irrespective of setting, you will be immediately notified of new vulnerabilities"
  default     = "24 hours"
}

variable "scan_schedule" {
  description = "schedule for running domain-protect scans, e.g. 60 minutes, does not affect frequency of regular Slack reports"
  default     = "60 minutes"
}

variable "scan_schedule_nonprod" {
  description = "schedule for running domain-protect scans in non-prod, reduced to save costs, e.g. 12 hours"
  default     = "24 hours"
}

variable "update_schedule" {
  description = "schedule for running domain-protect update function, e.g. 60 minutes"
  default     = "3 hours"
}

variable "update_schedule_nonprod" {
  description = "schedule for running domain-protect update function in non-prod, e.g. 12 hours"
  default     = "24 hours"
}

variable "ip_scan_schedule" {
  description = "schedule for IP address scanning used in A record checks"
  default     = "24 hours"
}

variable "ip_scan_schedule_nonprod" {
  description = "schedule for IP address scans in non-prod, reduced to save costs, e.g. 24 hours"
  default     = "24 hours"
}

variable "stats_schedule" {
  description = "Cron schedule for the stats message"
  default     = "cron(0 9 1 * ? *)" # 9am on the first of the month
}

variable "lambdas" {
  description = "list of names of Lambda files in the lambda/code folder"
  default     = ["current", "update"]
  type        = list(any)
}

variable "takeover" {
  description = "Create supported resource types to prevent malicious subdomain takeover"
  default     = true
}

variable "update_lambdas" {
  description = "list of Cloudflare Lambda functions updating vulnerability status"
  default     = ["update"]
  type        = list(any)
}

variable "production_workspace" {
  description = "Terraform workspace for production - takeover is only turned on in this environment"
  default     = "prod"
}

variable "runtime" {
  description = "Lambda language runtime"
  default     = "python3.9"
}

variable "memory_size" {
  description = "Memory allocation for scanning Lambda functions"
  default     = 128
}

variable "memory_size_slack" {
  description = "Memory allocation for Slack Lambda functions"
  default     = 128
}
variable "slack_channels" {
  description = "List of Slack Channels - enter in tfvars file"
  default     = []
  type        = list(any)
}

variable "slack_channels_dev" {
  description = "List of Slack Channels to use for testing purposes with dev environment - enter in tfvars file"
  default     = []
  type        = list(any)
}

variable "slack_webhook_urls" {
  description = "List of Slack webhook URLs, in the same order as the slack_channels list - enter in tfvars file"
  default     = []
  type        = list(any)
}

variable "slack_emoji" {
  description = "Slack emoji"
  default     = ":warning:"
}

variable "slack_fix_emoji" {
  description = "Slack fix emoji"
  default     = ":white_check_mark:"
}

variable "slack_new_emoji" {
  description = "Slack emoji for new vulnerability"
  default     = ":octagonal_sign:"
}

variable "slack_username" {
  description = "Slack username appearing in the from field in the Slack message"
  default     = "Domain Protect"
}

variable "bugcrowd" {
  description = "Set to enabled for Bugcrowd integration"
  default     = "disabled"
}

variable "bugcrowd_api_key" {
  description = "Bugcrowd API token"
  default     = ""
}

variable "bugcrowd_email" {
  description = "Email address of Bugcrowd researcher service account"
  default     = ""
}

variable "bugcrowd_state" {
  description = "State in which issue is created, e.g. new, triaged, unresolved, resolved"
  default     = "unresolved"
}

variable "cloudflare" {
  description = "Set to true to enable CloudFlare"
  default     = false
}

variable "cf_api_key" {
  description = "Cloudflare API token"
  default     = ""
}

variable "cloudflare_lambdas" {
  description = "list of names of Lambda files in the lambda-cloudflare/code folder"
  default     = ["cloudflare-scan"]
  type        = list(any)
}

variable "rcu" {
  description = "DynamoDB Read Capacity Units for vulnerability database"
  default     = 3
}

variable "wcu" {
  description = "DynamoDB Write Capacity Units for vulnerability database"
  default     = 2
}

variable "ip_address" {
  description = "Set to true to enable A record checks using IP address scans"
  default     = false
}

variable "allowed_regions" {
  description = "If SCPs block certain regions across all accounts, optionally replace with string formatted list of allowed regions"
  default     = "['all']" # example "['eu-west-1', 'us-east-1']"
}
