resource "aws_dynamodb_table" "vulnerable_domains" {
  # checkov:skip=CKV2_AWS_16: Auto Scaling more expensive than Provisioned, and not needed in this case with very low utilisation

  name           = "${replace(title(replace(var.project, "-", " ")), " ", "")}VulnerableDomains${title(var.environment)}"
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

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = var.kms_arn
  }

  tags = {
    Name = "${var.project}-vulnerable-domains-${var.environment}"
  }
}
