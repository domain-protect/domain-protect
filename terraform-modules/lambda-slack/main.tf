data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/code/notify"
  output_path = "${path.module}/build/notify.zip"
}

resource "aws_lambda_function" "lambda" {
  count            = length(var.slack_channels)
  filename         = "${path.module}/build/notify.zip"
  function_name    = "${var.project}-slack-${element(var.slack_channels, count.index)}-${local.env}"
  description      = "${var.project} Lambda function posting to ${element(var.slack_channels, count.index)} Slack channel"
  role             = var.lambda_role_arn
  handler          = "notify.lambda_handler"
  kms_key_arn      = var.kms_arn
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = var.runtime
  timeout          = var.timeout
  publish          = true

  environment {
    variables = {
      SLACK_CHANNEL     = element(var.slack_channels, count.index)
      SLACK_WEBHOOK_URL = element(var.slack_webhook_urls, count.index)
      SLACK_EMOJI       = var.slack_emoji
      SLACK_USERNAME    = var.slack_username
      PROJECT           = var.project
    }
  }
}

resource "aws_lambda_alias" "lambda" {
  count            = length(var.slack_channels)
  name             = "${var.project}-slack-${var.slack_channels[count.index]}-${local.env}"
  description      = "Alias for ${var.project}-${element(var.slack_channels, count.index)}-${local.env}"
  function_name    = aws_lambda_function.lambda[count.index].function_name
  function_version = "$LATEST"
}

resource "aws_lambda_permission" "sns" {
  count         = length(var.slack_channels)
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda[count.index].function_name
  principal     = "sns.amazonaws.com"
  source_arn    = var.sns_topic_arn
}

resource "aws_sns_topic_subscription" "lambda_subscription" {
  count     = length(var.slack_channels)
  topic_arn = var.sns_topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.lambda[count.index].arn
}
