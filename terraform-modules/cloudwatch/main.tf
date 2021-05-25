resource "aws_cloudwatch_event_rule" "scheduled_event" {
  count               = length(var.lambda_function_names)
  name                = "${var.project}-${var.lambda_function_names[count.index]}"
  description         = "Triggers ${var.project} lambda functions according to schedule"
  schedule_expression = "rate(${var.schedule})"
}

resource "aws_cloudwatch_event_target" "scheduled_event" {
  count     = length(var.lambda_function_names)
  rule      = aws_cloudwatch_event_rule.scheduled_event[count.index].name
  target_id = "lambda"
  arn       = var.lambda_function_arns[count.index]
}

resource "aws_lambda_permission" "allow_cloudwatch_to_invoke_lambda" {
  count         = length(var.lambda_function_names)
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_names[count.index]
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scheduled_event[count.index].arn
}