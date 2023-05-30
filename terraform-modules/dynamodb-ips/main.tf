resource "aws_dynamodb_table" "ips" {
  name         = local.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "IP"

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
