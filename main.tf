module "kms" {
  source      = "./terraform-modules/kms"
  project     = var.project
  region      = var.region
  environment = local.env
}

module "lambda-role" {
  source                   = "./terraform-modules/iam"
  project                  = var.project
  region                   = var.region
  security_audit_role_name = var.security_audit_role_name
  kms_arn                  = module.kms.kms_arn
  permissions_boundary_arn = var.permissions_boundary_arn
  environment              = local.env
}

module "lambda-slack" {
  source             = "./terraform-modules/lambda-slack"
  runtime            = var.runtime
  platform           = var.platform
  memory_size        = var.memory_size_slack
  project            = var.project
  lambda_role_arn    = module.lambda-role.lambda_role_arn
  kms_arn            = module.kms.kms_arn
  sns_topic_arn      = module.sns.sns_topic_arn
  dlq_sns_topic_arn  = module.sns-dead-letter-queue.sns_topic_arn
  slack_channels     = local.env == "dev" ? var.slack_channels_dev : var.slack_channels
  slack_webhook_urls = local.env == "dev" && length(var.slack_webhook_urls_dev) > 0 ? var.slack_webhook_urls_dev : var.slack_webhook_urls
  slack_webhook_type = var.slack_webhook_type
  slack_emoji        = var.slack_emoji
  slack_fix_emoji    = var.slack_fix_emoji
  slack_new_emoji    = var.slack_new_emoji
  slack_username     = var.slack_username
  environment        = local.env
}

module "lambda" {
  source                   = "./terraform-modules/lambda"
  lambdas                  = var.lambdas
  runtime                  = var.runtime
  platform                 = var.platform
  memory_size              = var.memory_size
  project                  = var.project
  security_audit_role_name = var.security_audit_role_name
  external_id              = var.external_id
  org_primary_account      = var.org_primary_account
  lambda_role_arn          = module.lambda-role.lambda_role_arn
  kms_arn                  = module.kms.kms_arn
  sns_topic_arn            = module.sns.sns_topic_arn
  dlq_sns_topic_arn        = module.sns-dead-letter-queue.sns_topic_arn
  state_machine_arn        = module.step-function.state_machine_arn
  allowed_regions          = var.allowed_regions
  ip_time_limit            = var.ip_time_limit
  environment              = local.env
}

module "lambda-accounts" {
  source                   = "./terraform-modules/lambda-accounts"
  lambdas                  = ["accounts"]
  runtime                  = var.runtime
  platform                 = var.platform
  memory_size              = var.memory_size
  project                  = var.project
  security_audit_role_name = var.security_audit_role_name
  external_id              = var.external_id
  org_primary_account      = var.org_primary_account
  lambda_role_arn          = module.accounts-role.lambda_role_arn
  kms_arn                  = module.kms.kms_arn
  sns_topic_arn            = module.sns.sns_topic_arn
  dlq_sns_topic_arn        = module.sns-dead-letter-queue.sns_topic_arn
  state_machine_arn        = module.step-function.state_machine_arn
  environment              = local.env
}

module "accounts-role" {
  source                   = "./terraform-modules/iam"
  project                  = var.project
  region                   = var.region
  security_audit_role_name = var.security_audit_role_name
  kms_arn                  = module.kms.kms_arn
  state_machine_arn        = module.step-function.state_machine_arn
  policy                   = "accounts"
  permissions_boundary_arn = var.permissions_boundary_arn
  environment              = local.env
}

module "lambda-scan" {
  source                   = "./terraform-modules/lambda-scan"
  lambdas                  = ["scan"]
  runtime                  = var.runtime
  platform                 = var.platform
  memory_size              = var.memory_size
  project                  = var.project
  security_audit_role_name = var.security_audit_role_name
  external_id              = var.external_id
  org_primary_account      = var.org_primary_account
  lambda_role_arn          = module.lambda-role.lambda_role_arn
  kms_arn                  = module.kms.kms_arn
  sns_topic_arn            = module.sns.sns_topic_arn
  dlq_sns_topic_arn        = module.sns-dead-letter-queue.sns_topic_arn
  bugcrowd                 = var.bugcrowd
  bugcrowd_api_key         = var.bugcrowd_api_key
  bugcrowd_email           = var.bugcrowd_email
  bugcrowd_state           = var.bugcrowd_state
  hackerone                = var.hackerone
  hackerone_api_token      = var.hackerone_api_token
  environment              = local.env
  production_environment   = local.production_environment
}

module "lambda-takeover" {
  #checkov:skip=CKV_AWS_274:role is ElasticBeanstalk admin, not full Administrator Access
  count             = local.takeover ? 1 : 0
  source            = "./terraform-modules/lambda-takeover"
  runtime           = var.runtime
  platform          = var.platform
  memory_size       = var.memory_size_slack
  project           = var.project
  lambda_role_arn   = module.takeover-role.*.lambda_role_arn[0]
  kms_arn           = module.kms.kms_arn
  sns_topic_arn     = module.sns.sns_topic_arn
  dlq_sns_topic_arn = module.sns-dead-letter-queue.sns_topic_arn
  environment       = local.env
}

module "takeover-role" {
  count                    = local.takeover ? 1 : 0
  source                   = "./terraform-modules/iam"
  project                  = var.project
  region                   = var.region
  security_audit_role_name = var.security_audit_role_name
  kms_arn                  = module.kms.kms_arn
  takeover                 = local.takeover
  policy                   = "takeover"
  permissions_boundary_arn = var.permissions_boundary_arn
  environment              = local.env
}

module "lambda-resources" {
  count             = local.takeover ? 1 : 0
  source            = "./terraform-modules/lambda-resources"
  lambdas           = ["resources"]
  runtime           = var.runtime
  memory_size       = var.memory_size_slack
  project           = var.project
  lambda_role_arn   = module.resources-role.*.lambda_role_arn[0]
  kms_arn           = module.kms.kms_arn
  sns_topic_arn     = module.sns.sns_topic_arn
  dlq_sns_topic_arn = module.sns-dead-letter-queue.sns_topic_arn
  environment       = local.env
}

module "resources-role" {
  count                    = local.takeover ? 1 : 0
  source                   = "./terraform-modules/iam"
  project                  = var.project
  region                   = var.region
  security_audit_role_name = var.security_audit_role_name
  kms_arn                  = module.kms.kms_arn
  policy                   = "resources"
  permissions_boundary_arn = var.permissions_boundary_arn
  environment              = local.env
}

module "cloudwatch-event" {
  source                      = "./terraform-modules/cloudwatch"
  project                     = var.project
  lambda_function_arns        = module.lambda.lambda_function_arns
  lambda_function_names       = module.lambda.lambda_function_names
  lambda_function_alias_names = module.lambda.lambda_function_alias_names
  schedule                    = var.reports_schedule
  takeover                    = local.takeover
  update_schedule             = local.env == local.production_environment ? var.update_schedule : var.update_schedule_nonprod
  update_lambdas              = var.update_lambdas
  environment                 = local.env
}

module "resources-event" {
  count                       = local.takeover ? 1 : 0
  source                      = "./terraform-modules/cloudwatch"
  project                     = var.project
  lambda_function_arns        = module.lambda-resources[0].lambda_function_arns
  lambda_function_names       = module.lambda-resources[0].lambda_function_names
  lambda_function_alias_names = module.lambda-resources[0].lambda_function_alias_names
  schedule                    = var.reports_schedule
  takeover                    = local.takeover
  update_schedule             = local.env == local.production_environment ? var.scan_schedule : var.scan_schedule_nonprod
  update_lambdas              = var.update_lambdas
  environment                 = local.env
}

module "accounts-event" {
  source                      = "./terraform-modules/cloudwatch"
  project                     = var.project
  lambda_function_arns        = module.lambda-accounts.lambda_function_arns
  lambda_function_names       = module.lambda-accounts.lambda_function_names
  lambda_function_alias_names = module.lambda-accounts.lambda_function_alias_names
  schedule                    = local.env == local.production_environment ? var.scan_schedule : var.scan_schedule_nonprod
  takeover                    = local.takeover
  update_schedule             = local.env == local.production_environment ? var.scan_schedule : var.scan_schedule_nonprod
  update_lambdas              = var.update_lambdas
  environment                 = local.env
}

module "sns" {
  source      = "./terraform-modules/sns"
  project     = var.project
  region      = var.region
  kms_arn     = module.kms.kms_arn
  environment = local.env
}

module "sns-dead-letter-queue" {
  source            = "./terraform-modules/sns"
  project           = var.project
  region            = var.region
  dead_letter_queue = true
  kms_arn           = module.kms.kms_arn
  environment       = local.env
}

module "lambda-cloudflare" {
  count                    = var.cloudflare ? 1 : 0
  source                   = "./terraform-modules/lambda-cloudflare"
  lambdas                  = var.cloudflare_lambdas
  runtime                  = var.runtime
  platform                 = var.platform
  memory_size              = var.memory_size
  project                  = var.project
  cf_api_key               = var.cf_api_key
  lambda_role_arn          = module.lambda-role.lambda_role_arn
  kms_arn                  = module.kms.kms_arn
  security_audit_role_name = var.security_audit_role_name
  external_id              = var.external_id
  org_primary_account      = var.org_primary_account
  sns_topic_arn            = module.sns.sns_topic_arn
  dlq_sns_topic_arn        = module.sns-dead-letter-queue.sns_topic_arn
  production_environment   = local.production_environment
  bugcrowd                 = var.bugcrowd
  bugcrowd_api_key         = var.bugcrowd_api_key
  bugcrowd_email           = var.bugcrowd_email
  bugcrowd_state           = var.bugcrowd_state
  hackerone                = var.hackerone
  hackerone_api_token      = var.hackerone_api_token
  environment              = local.env
}

module "cloudflare-event" {
  count                       = var.cloudflare ? 1 : 0
  source                      = "./terraform-modules/cloudwatch"
  project                     = var.project
  lambda_function_arns        = module.lambda-cloudflare[0].lambda_function_arns
  lambda_function_names       = module.lambda-cloudflare[0].lambda_function_names
  lambda_function_alias_names = module.lambda-cloudflare[0].lambda_function_alias_names
  schedule                    = local.env == local.production_environment ? var.scan_schedule : var.scan_schedule_nonprod
  takeover                    = local.takeover
  update_schedule             = local.env == local.production_environment ? var.scan_schedule : var.scan_schedule_nonprod
  update_lambdas              = var.update_lambdas
  environment                 = local.env
}

module "dynamodb" {
  source      = "./terraform-modules/dynamodb"
  project     = var.project
  kms_arn     = module.kms.kms_arn
  rcu         = var.rcu
  wcu         = var.wcu
  environment = local.env
}

module "step-function-role" {
  source                   = "./terraform-modules/iam"
  project                  = var.project
  region                   = var.region
  security_audit_role_name = var.security_audit_role_name
  kms_arn                  = module.kms.kms_arn
  policy                   = "state"
  assume_role_policy       = "state"
  permissions_boundary_arn = var.permissions_boundary_arn
  environment              = local.env
}

module "step-function" {
  source      = "./terraform-modules/step-function"
  project     = var.project
  lambda_arn  = module.lambda-scan.lambda_function_arns["scan"]
  role_arn    = module.step-function-role.lambda_role_arn
  kms_arn     = module.kms.kms_arn
  environment = local.env
}

module "dynamodb-ips" {
  count       = var.ip_address ? 1 : 0
  source      = "./terraform-modules/dynamodb-ips"
  project     = var.project
  kms_arn     = module.kms.kms_arn
  environment = local.env
}

module "step-function-ips" {
  count       = var.ip_address ? 1 : 0
  source      = "./terraform-modules/step-function"
  project     = var.project
  purpose     = "ips"
  lambda_arn  = module.lambda-scan-ips[0].lambda_function_arns["scan-ips"]
  role_arn    = module.step-function-role.lambda_role_arn
  kms_arn     = module.kms.kms_arn
  environment = local.env
}

module "lambda-role-ips" {
  count                    = var.ip_address ? 1 : 0
  source                   = "./terraform-modules/iam"
  project                  = var.project
  region                   = var.region
  security_audit_role_name = var.security_audit_role_name
  kms_arn                  = module.kms.kms_arn
  policy                   = "lambda"
  role_name                = "lambda-ips"
  permissions_boundary_arn = var.permissions_boundary_arn
  environment              = local.env
}

module "lambda-scan-ips" {
  count                    = var.ip_address ? 1 : 0
  source                   = "./terraform-modules/lambda-scan-ips"
  lambdas                  = ["scan-ips"]
  runtime                  = var.runtime
  platform                 = var.platform
  memory_size              = var.memory_size
  project                  = var.project
  security_audit_role_name = var.security_audit_role_name
  external_id              = var.external_id
  org_primary_account      = var.org_primary_account
  lambda_role_arn          = module.lambda-role-ips[0].lambda_role_arn
  kms_arn                  = module.kms.kms_arn
  sns_topic_arn            = module.sns.sns_topic_arn
  dlq_sns_topic_arn        = module.sns-dead-letter-queue.sns_topic_arn
  production_environment   = local.production_environment
  allowed_regions          = var.allowed_regions
  ip_time_limit            = var.ip_time_limit
  bugcrowd                 = var.bugcrowd
  bugcrowd_api_key         = var.bugcrowd_api_key
  bugcrowd_email           = var.bugcrowd_email
  bugcrowd_state           = var.bugcrowd_state
  hackerone                = var.hackerone
  hackerone_api_token      = var.hackerone_api_token
  environment              = local.env
}

module "accounts-role-ips" {
  count                    = var.ip_address ? 1 : 0
  source                   = "./terraform-modules/iam"
  project                  = var.project
  region                   = var.region
  security_audit_role_name = var.security_audit_role_name
  kms_arn                  = module.kms.kms_arn
  state_machine_arn        = module.step-function-ips[0].state_machine_arn
  policy                   = "accounts"
  role_name                = "accounts-ips"
  permissions_boundary_arn = var.permissions_boundary_arn
  environment              = local.env
}

module "lambda-accounts-ips" {
  count                    = var.ip_address ? 1 : 0
  source                   = "./terraform-modules/lambda-accounts"
  lambdas                  = ["accounts-ips"]
  runtime                  = var.runtime
  platform                 = var.platform
  memory_size              = var.memory_size
  project                  = var.project
  security_audit_role_name = var.security_audit_role_name
  external_id              = var.external_id
  org_primary_account      = var.org_primary_account
  lambda_role_arn          = module.accounts-role-ips[0].lambda_role_arn
  kms_arn                  = module.kms.kms_arn
  sns_topic_arn            = module.sns.sns_topic_arn
  dlq_sns_topic_arn        = module.sns-dead-letter-queue.sns_topic_arn
  state_machine_arn        = module.step-function-ips[0].state_machine_arn
  environment              = local.env
}

module "accounts-event-ips" {
  count                       = var.ip_address ? 1 : 0
  source                      = "./terraform-modules/cloudwatch"
  project                     = var.project
  lambda_function_arns        = module.lambda-accounts-ips[0].lambda_function_arns
  lambda_function_names       = module.lambda-accounts-ips[0].lambda_function_names
  lambda_function_alias_names = module.lambda-accounts-ips[0].lambda_function_alias_names
  schedule                    = local.env == local.production_environment ? var.ip_scan_schedule : var.ip_scan_schedule_nonprod
  takeover                    = local.takeover
  update_schedule             = local.env == local.production_environment ? var.ip_scan_schedule : var.ip_scan_schedule_nonprod
  update_lambdas              = var.update_lambdas
  environment                 = local.env
}

module "lamdba-stats" {
  source                   = "./terraform-modules/lambda-stats"
  runtime                  = var.runtime
  platform                 = var.platform
  memory_size              = var.memory_size
  project                  = var.project
  kms_arn                  = module.kms.kms_arn
  lambda_role_arn          = module.lambda-role.lambda_role_arn
  sns_topic_arn            = module.sns.sns_topic_arn
  dlq_sns_topic_arn        = module.sns-dead-letter-queue.sns_topic_arn
  schedule_expression      = var.stats_schedule
  org_primary_account      = var.org_primary_account
  security_audit_role_name = var.security_audit_role_name
  external_id              = var.external_id
  environment              = local.env
}
