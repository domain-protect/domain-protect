locals {
  env = lower(terraform.workspace)

  lambda_file_names = [for l in var.lambdas : replace(l, "-", "_")]
}
