resource "aws_iam_role" "lambda" {
  name                = "${var.project}-${local.role_name}-${local.env}"
  assume_role_policy  = templatefile("${path.module}/templates/assume_role.json.tpl", {})
  managed_policy_arns = var.takeover ? ["arn:aws:iam::aws:policy/AdministratorAccess-AWSElasticBeanstalk", "arn:aws:iam::aws:policy/AmazonS3FullAccess", "arn:aws:iam::aws:policy/AWSCloudFormationFullAccess"] : []
}

resource "aws_iam_role_policy" "lambda" {
  name   = "${var.project}-${var.policy}-${local.env}"
  role   = aws_iam_role.lambda.id
  policy = templatefile("${path.module}/templates/${var.policy}_policy.json.tpl", { security_audit_role_name = var.security_audit_role_name, project = var.project, env = local.env, kms_arn = var.kms_arn })
}
