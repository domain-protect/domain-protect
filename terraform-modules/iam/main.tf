resource "aws_iam_role" "lambda" {
  name = "${var.project}-${local.role_name}-${var.env}"
  assume_role_policy = templatefile("${path.module}/templates/${var.assume_role_policy}_role.json.tpl", {
    project = var.project,
  })
  managed_policy_arns  = var.takeover ? ["arn:aws:iam::aws:policy/AmazonVPCFullAccess", "arn:aws:iam::aws:policy/AdministratorAccess-AWSElasticBeanstalk", "arn:aws:iam::aws:policy/AmazonS3FullAccess", "arn:aws:iam::aws:policy/AWSCloudFormationFullAccess"] : []
  permissions_boundary = var.permissions_boundary_arn
}

resource "aws_iam_role_policy" "lambda" {
  name = "${var.project}-${local.role_policy_name}-${var.env}"
  role = aws_iam_role.lambda.id
  policy = templatefile("${path.module}/templates/${var.policy}_policy.json.tpl", {
    security_audit_role_name = var.security_audit_role_name,
    project                  = var.project,
    env                      = var.env,
    kms_arn                  = var.kms_arn,
    ddb_table_arn            = local.dynamodb_arn,
    ddb_ip_table_arn         = local.dynamodb_ip_arn,
    state_machine_arn        = var.state_machine_arn,
  })
}
