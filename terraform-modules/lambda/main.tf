resource "null_resource" "install_python_dependencies" {

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
  count       = length(var.lambdas)
  depends_on  = [null_resource.install_python_dependencies]
  type        = "zip"
  source_dir  = "${path.module}/build/lambda_dist_pkg_${var.lambdas[count.index]}"
  output_path = "${path.module}/build/${var.lambdas[count.index]}.zip"
}

resource "aws_lambda_function" "lambda" {
  count            = length(var.lambdas)
  filename         = "${path.module}/build/${var.lambdas[count.index]}.zip"
  function_name    = "${var.project}-${var.lambdas[count.index]}-${local.env}"
  description      = "${var.project} ${var.lambdas[count.index]} Lambda function"
  role             = var.lambda_role_arn
  handler          = "${var.lambdas[count.index]}.lambda_handler"
  kms_key_arn      = var.kms_arn
  source_code_hash = data.archive_file.lambda_zip[count.index].output_base64sha256
  runtime          = var.runtime
  timeout          = var.timeout
  publish          = true

  environment {
    variables = {
      ORG_PRIMARY_ACCOUNT      = var.org_primary_account
      SECURITY_AUDIT_ROLE_NAME = var.security_audit_role_name
      EXTERNAL_ID              = var.external_id
      PROJECT                  = var.project
      SNS_TOPIC_ARN            = var.sns_topic_arn
    }
  }
}

resource "aws_lambda_alias" "lambda" {
  count            = length(var.lambdas)
  name             = "${var.project}-${var.lambdas[count.index]}-${local.env}"
  description      = "Alias for ${var.project}-${var.lambdas[count.index]}s-${local.env}"
  function_name    = aws_lambda_function.lambda[count.index].function_name
  function_version = "$LATEST"
}
