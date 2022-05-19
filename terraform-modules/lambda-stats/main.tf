data "archive_file" "lambda_zip" {
  depends_on  = [null_resource.install_python_dependencies]
  type        = "zip"
  source_dir  = "${path.module}/build/lambda_dist_pkg_stats"
  output_path = "${path.module}/build/stats.zip"
}

resource "null_resource" "install_python_dependencies" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "${path.module}/scripts/create-package.sh"

    environment = {
      source_code_path = "${path.module}/code"
      function_name    = "stats"
      path_module      = path.module
      runtime          = var.runtime
      path_cwd         = path.cwd
    }
  }
}

resource "aws_lambda_function" "lambda" {
  # checkov:skip=CKV_AWS_115: concurrency limit on individual Lambda function not required
  # checkov:skip=CKV_AWS_117: not configured inside VPC as no handling of confidential data

  count            = length(var.slack_channels)
  filename         = "${path.module}/build/stats.zip"
  function_name    = "${var.project}-stats-slack-${element(var.slack_channels, count.index)}-${local.env}"
  description      = "${var.project} Lambda function posting stats to ${element(var.slack_channels, count.index)} Slack channel"
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
      SLACK_CHANNEL       = element(var.slack_channels, count.index)
      SLACK_WEBHOOK_URL   = element(var.slack_webhook_urls, count.index)
      SLACK_EMOJI         = var.slack_emoji
      SLACK_USERNAME      = var.slack_username
      PROJECT             = var.project
      TERRAFORM_WORKSPACE = local.env
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
  count            = length(var.slack_channels)
  name             = "${var.project}-slack-${var.slack_channels[count.index]}-${local.env}"
  description      = "Alias for ${var.project}-${element(var.slack_channels, count.index)}-${local.env}"
  function_name    = aws_lambda_function.lambda[count.index].function_name
  function_version = "$LATEST"
}

resource "aws_cloudwatch_event_rule" "first_day_of_month" {
  name                = "first-day-of-month"
  description         = "Fires on the first of the month at 9AM"
  schedule_expression = "cron(0 9 1 * ? *)" # 9am on the first of the month
}

resource "aws_cloudwatch_event_target" "run_lambda_on_first" {
  count = length(var.slack_channels)
  rule  = aws_cloudwatch_event_rule.first_day_of_month.name
  arn   = aws_lambda_function.lambda[count.index].arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_stats" {
  count         = length(var.slack_channels)
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda[count.index].function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.first_day_of_month.arn
}
