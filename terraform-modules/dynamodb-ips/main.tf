resource "aws_dynamodb_table" "ips" {
  # checkov:skip=CKV2_AWS_16: Auto Scaling more expensive than Provisioned, and not needed in this case with very low utilisation

  name           = local.table_name
  billing_mode   = "PROVISIONED"
  read_capacity  = var.rcu
  write_capacity = var.wcu
  hash_key       = "IP"

  attribute {
    name = "IP"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = var.kms_arn
  }

  tags = {
    Name = "${var.project}-ips-${local.env}"
  }
}