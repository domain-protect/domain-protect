module "kms" {
  source  = "./terraform-modules/kms"
  project = var.project
}

module "lambda-role" {
  source                   = "./terraform-modules/iam"
  project                  = var.project
  security_audit_role_name = var.security_audit_role_name
  kms_arn                  = module.kms.kms_arn
}

module "lambda-slack" {
  source             = "./terraform-modules/lambda-slack"
  runtime            = var.runtime
  project            = var.project
  lambda_role_arn    = module.lambda-role.lambda_role_arn
  kms_arn            = module.kms.kms_arn
  sns_topic_arn      = module.sns.sns_topic_arn
  slack_channels     = local.env == "dev" ? local.slack_channels_dev : local.slack_channels
  slack_webhook_urls = local.slack_webhook_urls
  slack_emoji        = var.slack_emoji
  slack_username     = var.slack_username
}

module "lambda" {
  source                   = "./terraform-modules/lambda"
  lambdas                  = var.lambdas
  runtime                  = var.runtime
  project                  = var.project
  security_audit_role_name = var.security_audit_role_name
  external_id              = var.external_id
  org_primary_account      = var.org_primary_account
  lambda_role_arn          = module.lambda-role.lambda_role_arn
  kms_arn                  = module.kms.kms_arn
  sns_topic_arn            = module.sns.sns_topic_arn
}

module "cloudwatch-event" {
  source                      = "./terraform-modules/cloudwatch"
  project                     = var.project
  lambda_function_arns        = module.lambda.lambda_function_arns
  lambda_function_names       = module.lambda.lambda_function_names
  lambda_function_alias_names = module.lambda.lambda_function_alias_names
  schedule                    = var.schedule
}

module "sns" {
  source  = "./terraform-modules/sns"
  project = var.project
  region  = var.region
  kms_arn = module.kms.kms_arn
}