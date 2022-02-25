output "ddb_table_arn" {
  value = aws_dynamodb_table.vulnerable_domains.arn
}
