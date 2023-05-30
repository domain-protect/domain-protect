resource "aws_kms_key" "encryption" {
  description             = "Encryption of ${var.project}-${local.env} resources"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  policy                  = templatefile("${path.module}/templates/${var.kms_policy}.json.tpl", { account_id = data.aws_caller_identity.current.account_id, region = var.region })
}

resource "aws_kms_alias" "encryption" {
  name          = "alias/${var.project}-${local.env}"
  target_key_id = aws_kms_key.encryption.key_id
}
