data "archive_file" "lambda_zip" {
  depends_on  = [null_resource.install_python_dependencies]
  type        = "zip"
  source_dir  = "${path.cwd}/build/lambda_dist_pkg_takeover"
  output_path = "${path.cwd}/build/takeover.zip"
}

resource "null_resource" "install_python_dependencies" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "${path.cwd}/scripts/lambda-build/create-package.sh"

    environment = {
      source_code_path = "${path.cwd}/lambda_code"
      function_name    = "takeover"
      runtime          = var.runtime
      platform         = var.platform
      path_cwd         = path.cwd
    }
  }
}

resource "random_string" "suffix" {
  length    = 8
  min_lower = 8
}

resource "aws_lambda_function" "lambda" {
  # checkov:skip=CKV_AWS_115: concurrency limit on individual Lambda function not required
  # checkov:skip=CKV_AWS_117: not configured inside VPC as no handling of confidential data
  # checkov:skip=CKV_AWS_272: code-signing not validated to avoid need for signing profile

  filename         = "${path.cwd}/build/takeover.zip"
  function_name    = "${var.project}-takeover-${var.environment}"
  description      = "${var.project} Lambda function to takeover vulnerable resources"
  role             = var.lambda_role_arn
  handler          = "takeover.lambda_handler"
  kms_key_arn      = var.kms_arn
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = var.runtime
  memory_size      = var.memory_size
  timeout          = var.timeout
  publish          = true

  environment {
    variables = {
      PROJECT       = var.project
      SNS_TOPIC_ARN = var.sns_topic_arn
      SUFFIX        = random_string.suffix.result
      ENVIRONMENT   = var.environment
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
  name             = "${var.project}-takeover-${var.environment}"
  description      = "Alias for ${var.project}-takeover-${var.environment}"
  function_name    = aws_lambda_function.lambda.function_name
  function_version = "$LATEST"
}

resource "aws_lambda_permission" "sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = var.sns_topic_arn
}

resource "aws_sns_topic_subscription" "lambda_subscription" {
  topic_arn = var.sns_topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.lambda.arn
}
