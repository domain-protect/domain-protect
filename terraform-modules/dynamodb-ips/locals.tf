locals {
  env        = lower(terraform.workspace)
  table_name = "${replace(title(replace(var.project, "-", " ")), " ", "")}IPs${title(local.env)}"
}
