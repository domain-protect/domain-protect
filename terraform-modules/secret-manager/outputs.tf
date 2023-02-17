output "secret_ids" {
  description = "Secret ids list"
  value       = [for k, v in aws_secretsmanager_secret.secret_name : v.id]
}

output "secret_arns" {
  description = "Secrets arns list"
  value       = [for v in aws_secretsmanager_secret.secret_name : v.arn]
}
