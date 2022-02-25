resource "aws_dynamodb_table" "vulnerable_domains" {
  name           = local.table_name
  billing_mode   = "PROVISIONED"
  read_capacity  = var.rcu
  write_capacity = var.wcu
  hash_key       = "Domain"
  range_key      = "FoundDateTime"

  attribute {
    name = "Domain"
    type = "S"
  }

  attribute {
    name = "FoundDateTime"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = var.kms_arn
  }

  tags = {
    Name = "${var.project}-vulnerable-domains-${local.env}"
  }
}