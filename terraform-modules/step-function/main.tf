resource "aws_cloudwatch_log_group" "log_group_for_sfn" {
  name              = "/aws/vendedlogs/states/${var.project}-${var.purpose}-${local.env}"
  kms_key_id        = var.kms_arn
  retention_in_days = var.retention_in_days
}

resource "aws_sfn_state_machine" "state_machine" {
  definition = templatefile("${path.module}/templates/default.json.tpl", { lambda_arn = var.lambda_arn })
  name       = "${var.project}-${var.purpose}-${local.env}"
  role_arn   = var.role_arn


  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.log_group_for_sfn.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }
}
