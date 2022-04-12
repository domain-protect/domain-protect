locals {
  env              = lower(terraform.workspace)
  role_name        = var.takeover ? "takeover" : local.role_policy_name
  role_policy_name = var.role_name == "policyname" ? var.policy : var.role_name
}