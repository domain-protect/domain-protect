resource "aws_sns_topic" "sns_topic" {
  name              = local.sns_topic_name
  display_name      = var.dead_letter_queue ? title(replace("${var.project}-dead-letter-queue-${local.env}", "-", " ")) : title(replace("${var.project}-${local.env}", "-", " "))
  policy            = templatefile("${path.module}/templates/${var.sns_policy}.json.tpl", { region = var.region, account_id = data.aws_caller_identity.current.account_id, sns_topic_name = local.sns_topic_name, project = var.project })
  kms_master_key_id = var.kms_arn
}
