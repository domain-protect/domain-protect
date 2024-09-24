moved {
  from = module.kms
  to   = module.domain_protect.module.kms
}

moved {
  from = module.lambda-role
  to   = module.domain_protect.module.lambda_role
}

moved {
  from = module.lambda-slack
  to   = module.domain_protect.module.lambda_slack
}

moved {
  from = module.lambda
  to   = module.domain_protect.module.lambda
}

moved {
  from = module.lambda-accounts
  to   = module.domain_protect.module.lambda_accounts
}

moved {
  from = module.accounts-role
  to   = module.domain_protect.module.accounts_role
}

moved {
  from = module.lambda-scan
  to   = module.domain_protect.module.lambda_scan
}

moved {
  from = module.lambda-takeover
  to   = module.domain_protect.module.lambda_takeover
}

moved {
  from = module.takeover-role
  to   = module.domain_protect.module.takeover_role
}

moved {
  from = module.lambda-resources
  to   = module.domain_protect.module.lambda_resources
}

moved {
  from = module.resources-role
  to   = module.domain_protect.module.resources_role
}

moved {
  from = module.cloudwatch-event
  to   = module.domain_protect.module.cloudwatch_event
}

moved {
  from = module.resources-event
  to   = module.domain_protect.module.resources_event
}

moved {
  from = module.accounts-event
  to   = module.domain_protect.module.accounts_event
}

moved {
  from = module.sns
  to   = module.domain_protect.module.sns
}

moved {
  from = module.sns-dead-letter-queue
  to   = module.domain_protect.module.sns_dead_letter_queue
}

moved {
  from = module.lambda-cloudflare
  to   = module.domain_protect.module.lambda_cloudflare
}

moved {
  from = module.cloudflare-event
  to   = module.domain_protect.module.cloudflare_event
}

moved {
  from = module.dynamodb
  to   = module.domain_protect.module.dynamodb
}

moved {
  from = module.step-function-role
  to   = module.domain_protect.module.step_function_role
}

moved {
  from = module.step-function
  to   = module.domain_protect.module.step_function
}

moved {
  from = module.dynamodb-ips
  to   = module.domain_protect.module.dynamodb_ips
}

moved {
  from = module.step-function-ips
  to   = module.domain_protect.module.step_function_ips
}

moved {
  from = module.lambda-role-ips
  to   = module.domain_protect.module.lambda_role_ips
}

moved {
  from = module.lambda-scan-ips
  to   = module.domain_protect.module.lambda_scan_ips
}

moved {
  from = module.accounts-role-ips
  to   = module.domain_protect.module.accounts_role_ips
}

moved {
  from = module.lambda-accounts-ips
  to   = module.domain_protect.module.lambda_accounts_ips
}

moved {
  from = module.accounts-event-ips
  to   = module.domain_protect.module.accounts_event_ips
}

moved {
  from = module.lamdba-stats
  to   = module.domain_protect.module.lamdba_stats
}
