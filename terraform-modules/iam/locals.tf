locals {
  env       = lower(terraform.workspace)
  role_name = var.takeover ? "takeover" : var.policy
}