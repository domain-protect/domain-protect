resource "null_resource" "install_python_dependencies" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "${path.cwd}/scripts/lambda-build/create-package-for-each.sh"

    environment = {
      source_code_path = "${path.cwd}/lambda_code"
      function_names   = join(":", local.lambda_file_names)
      runtime          = var.runtime
      path_cwd         = path.cwd
    }
  }
}

data "archive_file" "lambda_zip" {
  for_each = toset(local.lambda_file_names)

  depends_on  = [null_resource.install_python_dependencies]
  type        = "zip"
  source_dir  = "${path.cwd}/build/lambda_dist_pkg_${each.value}"
  output_path = "${path.cwd}/build/${each.value}.zip"
}

resource "aws_lambda_function" "lambda" {
  # checkov:skip=CKV_AWS_45: acceptable to set Cloudflare and Bugcrowd API tokens as environment variables
  # checkov:skip=CKV_AWS_115: concurrency limit on individual Lambda function not required
  # checkov:skip=CKV_AWS_117: not configured inside VPC as no handling of confidential data
  # checkov:skip=CKV_AWS_272: code-signing not validated to avoid need for signing profile

  for_each = toset(var.lambdas)

  filename         = "${path.cwd}/build/${replace(each.value, "-", "_")}.zip"
  function_name    = "${var.project}-${each.value}-${local.env}"
  description      = "${var.project} ${each.value} Lambda function"
  role             = var.lambda_role_arn
  handler          = "${each.value}.lambda_handler"
  kms_key_arn      = var.kms_arn
  source_code_hash = data.archive_file.lambda_zip[replace(each.value, "-", "_")].output_base64sha256
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

  dead_letter_config {
    target_arn = var.dlq_sns_topic_arn
  }

  tracing_config {
    mode = "Active"
  }
}

resource "aws_lambda_alias" "lambda" {
  for_each = toset(var.lambdas)

  name             = "${var.project}-${each.value}-${local.env}"
  description      = "Alias for ${var.project}-${each.value}s-${local.env}"
  function_name    = aws_lambda_function.lambda[each.key].function_name
  function_version = "$LATEST"
}
