locals {
  env            = lower(terraform.workspace)
  sns_topic_name = var.dead_letter_queue ? "${var.project}-dlq-${local.env}" : "${var.project}-${local.env}"
}