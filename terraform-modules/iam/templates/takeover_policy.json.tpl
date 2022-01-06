{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "WriteToCloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": [
        "arn:aws:logs:*:*:*"
      ]
    },
    {
      "Sid": "PutCloudWatchMetrics",
      "Effect": "Allow",
      "Action": "cloudwatch:PutMetricData",
      "Resource": "*"
    },
    {
      "Sid": "SNS",
      "Effect": "Allow",
      "Action": [
        "sns:Publish",
        "sns:Subscribe"
        ],
      "Resource": "arn:aws:sns:*:*:${project}-${env}"
    },
    {
      "Sid": "KMSforSNS",
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt",
        "kms:Encrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": "${kms_arn}"
    },
    {
      "Sid": "GetAccountName",
      "Effect": "Allow",
      "Action": [
        "iam:ListAccountAliases"
      ],
      "Resource": "*"
    },
    {
      "Sid": "IAMPermissionsForElasticBEanstalk",
      "Effect": "Allow",
      "Action": [
          "iam:AddRoleToInstanceProfile",
          "iam:AttachRolePolicy",
          "iam:CreateInstanceProfile", 
          "iam:CreateRole",
          "iam:DeleteInstanceProfile",
          "iam:DeleteRole",
          "iam:DetachRolePolicy",
          "iam:GetInstanceProfile",
          "iam:GetRole",
          "iam:GetRolePolicy",
          "iam:PassRole",
          "iam:RemoveRoleFromInstanceProfile",
          "iam:TagInstanceProfile",
          "iam:TagRole",
          "iam:UntagInstanceProfile",
          "iam:UntagRole",
          "iam:UpdateRole"
      ],
      "Resource": [
          "arn:aws:iam::409089539686:role/${project}*",
          "arn:aws:iam::409089539686:instance-profile/${project}*"
      ]
    }
  ]
}