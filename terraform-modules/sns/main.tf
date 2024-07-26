resource "aws_sns_topic" "sns_topic" {
  name              = var.dead_letter_queue ? "${var.project}-dlq-${var.env}" : "${var.project}-${var.env}"
  display_name      = var.dead_letter_queue ? title(replace("${var.project}-dead-letter-queue-${var.env}", "-", " ")) : title(replace("${var.project}-${var.env}", "-", " "))
  policy            = templatefile("${path.module}/templates/${var.sns_policy}.json.tpl", { region = var.region, account_id = data.aws_caller_identity.current.account_id, sns_topic_name = var.dead_letter_queue ? "${var.project}-dlq-${var.env}" : "${var.project}-${var.env}", project = var.project })
  kms_master_key_id = var.kms_arn
}
