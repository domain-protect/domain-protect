module "kms" {
  source  = "./terraform-modules/kms"
  project = var.project
}

module "lambda-role" {
  source                   = "./terraform-modules/iam"
  project                  = var.project
  security_audit_role_name = var.security_audit_role_name
  kms_arn                  = module.kms.kms_arn
  ddb_table_arn            = module.dynamodb.ddb_table_arn
}

module "lambda-slack" {
  source             = "./terraform-modules/lambda-slack"
  runtime            = var.runtime
  memory_size        = var.memory_size_slack
  project            = var.project
  lambda_role_arn    = module.lambda-role.lambda_role_arn
  kms_arn            = module.kms.kms_arn
  sns_topic_arn      = module.sns.sns_topic_arn
  slack_channels     = local.env == "dev" ? var.slack_channels_dev : var.slack_channels
  slack_webhook_urls = var.slack_webhook_urls
  slack_emoji        = var.slack_emoji
  slack_fix_emoji    = var.slack_fix_emoji
  slack_username     = var.slack_username
}

module "lambda" {
  source                   = "./terraform-modules/lambda"
  lambdas                  = var.lambdas
  runtime                  = var.runtime
  memory_size              = var.memory_size
  project                  = var.project
  security_audit_role_name = var.security_audit_role_name
  external_id              = var.external_id
  org_primary_account      = var.org_primary_account
  lambda_role_arn          = module.lambda-role.lambda_role_arn
  kms_arn                  = module.kms.kms_arn
  sns_topic_arn            = module.sns.sns_topic_arn
}

module "lambda-takeover" {
  count           = local.takeover ? 1 : 0
  source          = "./terraform-modules/lambda-takeover"
  runtime         = var.runtime
  memory_size     = var.memory_size_slack
  project         = var.project
  lambda_role_arn = module.takeover-role.*.lambda_role_arn[0]
  kms_arn         = module.kms.kms_arn
  sns_topic_arn   = module.sns.sns_topic_arn
}

module "takeover-role" {
  count                    = local.takeover ? 1 : 0
  source                   = "./terraform-modules/iam"
  project                  = var.project
  security_audit_role_name = var.security_audit_role_name
  kms_arn                  = module.kms.kms_arn
  ddb_table_arn            = module.dynamodb.ddb_table_arn
  takeover                 = local.takeover
  policy                   = "takeover"
}

module "lambda-resources" {
  count           = local.takeover ? 1 : 0
  source          = "./terraform-modules/lambda-resources"
  runtime         = var.runtime
  memory_size     = var.memory_size_slack
  project         = var.project
  lambda_role_arn = module.resources-role.*.lambda_role_arn[0]
  kms_arn         = module.kms.kms_arn
  sns_topic_arn   = module.sns.sns_topic_arn
}

module "resources-role" {
  count                    = local.takeover ? 1 : 0
  source                   = "./terraform-modules/iam"
  project                  = var.project
  security_audit_role_name = var.security_audit_role_name
  kms_arn                  = module.kms.kms_arn
  ddb_table_arn            = module.dynamodb.ddb_table_arn
  policy                   = "resources"
}

module "cloudwatch-event" {
  source                      = "./terraform-modules/cloudwatch"
  project                     = var.project
  lambda_function_arns        = module.lambda.lambda_function_arns
  lambda_function_names       = module.lambda.lambda_function_names
  lambda_function_alias_names = module.lambda.lambda_function_alias_names
  schedule                    = var.schedule
  takeover                    = local.takeover
  takeover_schedule           = var.takeover_schedule
  takeover_lambdas            = var.takeover_lambdas
}

module "resources-event" {
  count                       = local.takeover ? 1 : 0
  source                      = "./terraform-modules/cloudwatch"
  project                     = var.project
  lambda_function_arns        = module.lambda-resources[0].lambda_function_arns
  lambda_function_names       = module.lambda-resources[0].lambda_function_names
  lambda_function_alias_names = module.lambda-resources[0].lambda_function_alias_names
  schedule                    = var.schedule
  takeover                    = local.takeover
  takeover_schedule           = var.takeover_schedule
  takeover_lambdas            = var.takeover_lambdas
}

module "sns" {
  source  = "./terraform-modules/sns"
  project = var.project
  region  = var.region
  kms_arn = module.kms.kms_arn
}

module "lambda-cloudflare" {
  count                    = var.cloudflare ? 1 : 0
  source                   = "./terraform-modules/lambda-cloudflare"
  lambdas                  = var.cloudflare_lambdas
  runtime                  = var.runtime
  memory_size              = var.memory_size
  project                  = var.project
  cf_api_key               = var.cf_api_key
  lambda_role_arn          = module.lambda-role.lambda_role_arn
  kms_arn                  = module.kms.kms_arn
  security_audit_role_name = var.security_audit_role_name
  external_id              = var.external_id
  org_primary_account      = var.org_primary_account
  sns_topic_arn            = module.sns.sns_topic_arn
}

module "cloudflare-event" {
  count                       = var.cloudflare ? 1 : 0
  source                      = "./terraform-modules/cloudwatch"
  project                     = var.project
  lambda_function_arns        = module.lambda-cloudflare[0].lambda_function_arns
  lambda_function_names       = module.lambda-cloudflare[0].lambda_function_names
  lambda_function_alias_names = module.lambda-cloudflare[0].lambda_function_alias_names
  schedule                    = var.schedule
  takeover                    = local.takeover
  takeover_schedule           = var.takeover_schedule
  takeover_lambdas            = var.takeover_lambdas
}

module "dynamodb" {
  source  = "./terraform-modules/dynamodb"
  project = var.project
  kms_arn = module.kms.kms_arn
  rcu     = var.rcu
  wcu     = var.wcu
}
