locals {
  env      = lower(terraform.workspace)
  takeover = var.takeover == true && local.env == var.production_workspace ? true : false
}
