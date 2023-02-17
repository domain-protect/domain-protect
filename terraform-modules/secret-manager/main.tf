resource "random_string" "suffix" {
  count     = length(var.secret_values)
  length    = 8
  min_lower = 8
}

resource "aws_secretsmanager_secret" "secret_name" {
  count                   = length(var.secret_values)
  name                    = "${var.project}-${var.secret_type}-${random_string.suffix[count.index].result}"
  recovery_window_in_days = var.recovery_windows_in_days
  kms_key_id              = var.kms_arn
  description             = "${var.secret_type} value for ${var.project}"
  tags                    = var.tags
}

resource "aws_secretsmanager_secret_version" "secret_version_manual" {
  count         = var.manual_secret_upload ? length(var.secret_values) : 0
  secret_id     = element(aws_secretsmanager_secret.secret_name, count.index).id
  secret_string = element(var.secret_values, count.index)
  lifecycle {
    ignore_changes = [
      secret_id,
      secret_string
    ]
  }
}

resource "aws_secretsmanager_secret_version" "secret_version_auto" {
  count         = var.manual_secret_upload ? 0 : length(var.secret_values)
  secret_id     = element(aws_secretsmanager_secret.secret_name, count.index).id
  secret_string = element(var.secret_values, count.index)
  lifecycle {
    ignore_changes = [
      secret_id
    ]
  }
}
