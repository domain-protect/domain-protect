resource "null_resource" "install_python_dependencies" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "${path.module}/scripts/create-package.sh"

    environment = {
      source_code_path = "${path.module}/code"
      function_names   = join(":", var.lambdas)
      path_module      = path.module
      runtime          = var.runtime
      path_cwd         = path.cwd
    }
  }
}

data "archive_file" "lambda_zip" {
  for_each = toset(var.lambdas)

  depends_on  = [null_resource.install_python_dependencies]
  type        = "zip"
  source_dir  = "${path.module}/build/lambda_dist_pkg_${each.value}"
  output_path = "${path.module}/build/${each.value}.zip"
}

resource "aws_lambda_function" "lambda" {
  for_each = toset(var.lambdas)

  filename         = "${path.module}/build/${each.value}.zip"
  function_name    = "${var.project}-${each.value}-${local.env}"
  description      = "${var.project} ${each.value} Lambda function"
  role             = var.lambda_role_arn
  handler          = "${each.value}.lambda_handler"
  kms_key_arn      = var.kms_arn
  source_code_hash = data.archive_file.lambda_zip[each.key].output_base64sha256
  runtime          = var.runtime
  memory_size      = var.memory_size
  timeout          = var.timeout
  publish          = true

  environment {
    variables = {
      CF_API_KEY               = var.cf_api_key
      ORG_PRIMARY_ACCOUNT      = var.org_primary_account
      SECURITY_AUDIT_ROLE_NAME = var.security_audit_role_name
      EXTERNAL_ID              = var.external_id
      PROJECT                  = var.project
      SNS_TOPIC_ARN            = var.sns_topic_arn
      TERRAFORM_WORKSPACE      = local.env
      PRODUCTION_WORKSPACE     = var.production_workspace
      BUGCROWD                 = var.bugcrowd
      BUGCROWD_API_KEY         = var.bugcrowd_api_key
      BUGCROWD_EMAIL           = var.bugcrowd_email
      BUGCROWD_STATE           = var.bugcrowd_state
    }
  }
}

resource "aws_lambda_alias" "lambda" {
  for_each = toset(var.lambdas)

  name             = "${var.project}-${each.value}-${local.env}"
  description      = "Alias for ${var.project}-${each.value}s-${local.env}"
  function_name    = aws_lambda_function.lambda[each.key].function_name
  function_version = "$LATEST"
}
