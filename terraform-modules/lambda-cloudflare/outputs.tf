output "lambda_function_arns" {
  value = tomap({
    for k, l in aws_lambda_function.lambda : k => l.arn
  })
}

output "lambda_function_names" {
  value = tomap({
    for k, l in aws_lambda_function.lambda : k => l.function_name
  })
}

output "lambda_function_alias_names" {
  value = tomap({
    for k, l in aws_lambda_alias.lambda : k => l.name
  })
}
