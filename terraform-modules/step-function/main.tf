resource "aws_cloudwatch_log_group" "log_group_for_sfn" {
  name = "/aws/vendedlogs/states/${var.project}-scan-${local.env}"  
}

resource "aws_sfn_state_machine" "state_machine" {
  definition = templatefile("${path.module}/templates/scan.json.tpl", {lambda_arn = var.lambda_arn})
  name       = "${var.project}-scan-${local.env}"
  role_arn   = var.role_arn

  
  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.log_group_for_sfn.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }
}
