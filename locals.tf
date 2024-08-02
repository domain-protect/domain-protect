locals {
  env      = coalesce(var.environment, lower(terraform.workspace))
  takeover = var.takeover == true && local.env == var.production_workspace ? true : false
}
