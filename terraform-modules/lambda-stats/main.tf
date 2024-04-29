data "archive_file" "lambda_zip" {
  depends_on  = [null_resource.install_python_dependencies]
  type        = "zip"
  source_dir  = "${path.cwd}/build/lambda_dist_pkg_stats"
  output_path = "${path.cwd}/build/stats.zip"
}

resource "null_resource" "install_python_dependencies" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "${path.cwd}/scripts/lambda-build/create-package.sh"

    environment = {
      source_code_path = "${path.cwd}/lambda_code"
      function_name    = "stats"
      runtime          = var.runtime
      platform         = var.platform
      path_cwd         = path.cwd
    }
  }
}

resource "aws_lambda_function" "lambda" {
  # checkov:skip=CKV_AWS_115: concurrency limit on individual Lambda function not required
  # checkov:skip=CKV_AWS_117: not configured inside VPC as no handling of confidential data
  # checkov:skip=CKV_AWS_272: code-signing not validated to avoid need for signing profile

  filename         = "${path.cwd}/build/stats.zip"
  function_name    = "${var.project}-stats-${local.env}"
  description      = "${var.project} Lambda function posting stats to SNS"
  role             = var.lambda_role_arn
  handler          = "stats.lambda_handler"
  kms_key_arn      = var.kms_arn
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = var.runtime
  memory_size      = var.memory_size
  timeout          = var.timeout
  publish          = true

  environment {
    variables = {
      PROJECT                  = var.project
      TERRAFORM_WORKSPACE      = local.env
      ORG_PRIMARY_ACCOUNT      = var.org_primary_account
      SECURITY_AUDIT_ROLE_NAME = var.security_audit_role_name
      EXTERNAL_ID              = var.external_id
      SNS_TOPIC_ARN            = var.sns_topic_arn
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
  name             = "${var.project}-stats-${local.env}"
  description      = "Alias for ${var.project}-stats-${local.env}"
  function_name    = aws_lambda_function.lambda.function_name
  function_version = "$LATEST"
}

resource "aws_cloudwatch_event_rule" "first_day_of_month" {
  name                = "${var.project}-stats-${local.env}"
  description         = "Triggers ${var.project} lambda stats function according to schedule"
  schedule_expression = var.schedule_expression
}

resource "aws_cloudwatch_event_target" "run_lambda_on_first" {
  rule = aws_cloudwatch_event_rule.first_day_of_month.name
  arn  = aws_lambda_function.lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_stats" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.first_day_of_month.arn
}
