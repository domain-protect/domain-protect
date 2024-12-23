module "domain_protect" {
  source  = "domain-protect/domain-protect/aws"
  version = "0.5.1"

  project                  = var.project
  region                   = var.region
  org_primary_account      = var.org_primary_account
  security_audit_role_name = var.security_audit_role_name
  external_id              = var.external_id
  ip_time_limit            = var.ip_time_limit
  reports_schedule         = var.reports_schedule
  scan_schedule            = terraform.workspace == var.production_workspace ? var.scan_schedule : var.scan_schedule_nonprod
  update_schedule          = terraform.workspace == var.production_workspace ? var.update_schedule : var.update_schedule_nonprod
  ip_scan_schedule         = terraform.workspace == var.production_workspace ? var.ip_scan_schedule : var.ip_scan_schedule_nonprod
  stats_schedule           = var.stats_schedule
  lambdas                  = var.lambdas
  takeover                 = terraform.workspace == var.production_workspace ? var.takeover : false
  update_lambdas           = var.update_lambdas
  environment              = var.environment
  production_environment   = var.production_environment
  production_workspace     = var.production_workspace
  runtime                  = var.runtime
  platform                 = var.platform
  memory_size              = var.memory_size
  memory_size_slack        = var.memory_size_slack
  slack_channels           = terraform.workspace == var.production_workspace ? var.slack_channels : var.slack_channels_dev
  slack_webhook_urls       = terraform.workspace == var.production_workspace ? var.slack_webhook_urls : var.slack_webhook_urls_dev
  slack_webhook_type       = var.slack_webhook_type
  slack_emoji              = var.slack_emoji
  slack_fix_emoji          = var.slack_fix_emoji
  slack_new_emoji          = var.slack_new_emoji
  slack_username           = var.slack_username
  bugcrowd                 = var.bugcrowd
  bugcrowd_api_key         = var.bugcrowd_api_key
  bugcrowd_email           = var.bugcrowd_email
  bugcrowd_state           = var.bugcrowd_state
  hackerone                = var.hackerone
  hackerone_api_token      = var.hackerone_api_token
  cloudflare               = var.cloudflare
  cf_api_key               = var.cf_api_key
  cloudflare_lambdas       = var.cloudflare_lambdas
  rcu                      = var.rcu
  wcu                      = var.wcu
  ip_address               = var.ip_address
  allowed_regions          = var.allowed_regions
  permissions_boundary_arn = var.permissions_boundary_arn
}
