locals {
  role_name              = var.takeover ? "takeover" : local.role_policy_name
  role_policy_name       = var.role_name == "policyname" ? var.policy : var.role_name
  dynamodb_table_name    = "${replace(title(replace(var.project, "-", " ")), " ", "")}VulnerableDomains${title(var.env)}"
  dynamodb_ip_table_name = "${replace(title(replace(var.project, "-", " ")), " ", "")}IPs${title(var.env)}"
  account_id             = data.aws_caller_identity.current.account_id
  dynamodb_arn           = "arn:aws:dynamodb:${var.region}:${local.account_id}:table/${local.dynamodb_table_name}"
  dynamodb_ip_arn        = "arn:aws:dynamodb:${var.region}:${local.account_id}:table/${local.dynamodb_ip_table_name}"
}
