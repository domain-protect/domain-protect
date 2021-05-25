resource "aws_kms_key" "encryption" {
  description             = "Encryption of ${var.project}-${local.env} resources"
  deletion_window_in_days = 7
  enable_key_rotation     = true
}

resource "aws_kms_alias" "encryption" {
  name          = "alias/${var.project}-${local.env}"
  target_key_id = aws_kms_key.encryption.key_id
}