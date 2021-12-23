resource "aws_cloudwatch_event_rule" "scheduled_event" {
  for_each            = var.lambda_function_names
  
  name                = "${var.project}-${each.value}"
  description         = "Triggers ${var.project} lambda functions according to schedule"
  schedule_expression = "rate(${var.schedule})"
}

resource "aws_cloudwatch_event_target" "scheduled_event" {
  for_each  = var.lambda_function_arns

  rule      = aws_cloudwatch_event_rule.scheduled_event[each.key].name
  target_id = "lambda"
  arn       = each.value
}

resource "aws_lambda_permission" "allow_cloudwatch_to_invoke_lambda" {
  for_each      = var.lambda_function_alias_names

  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = each.value
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scheduled_event[each.key].arn
}