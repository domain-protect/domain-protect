locals {
  env                    = coalesce(var.environment, lower(terraform.workspace))
  production_environment = coalesce(var.production_workspace, var.production_environment)
  takeover               = var.takeover == true && local.env == var.production_workspace ? true : false
}
