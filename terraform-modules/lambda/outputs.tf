output "lambda_function_arns" {
  value = aws_lambda_function.lambda.*.arn
}

output "lambda_function_names" {
  value = aws_lambda_function.lambda.*.function_name
}

output "lambda_function_alias_names" {
  value = aws_lambda_alias.lambda.*.name
}