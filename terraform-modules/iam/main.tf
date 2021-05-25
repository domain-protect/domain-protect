resource "aws_iam_role" "lambda" {
  name               = "${var.project}-lambda-${local.env}"
  assume_role_policy = templatefile("${path.module}/templates/assume_role.json.tpl", {})
}

resource "aws_iam_role_policy" "lambda" {
  name   = "${var.project}-lambda-${local.env}"
  role   = aws_iam_role.lambda.id
  policy = templatefile("${path.module}/templates/lambda_policy.json.tpl", { security_audit_role_name = var.security_audit_role_name, project = var.project, env = local.env , kms_arn = var.kms_arn})
}
