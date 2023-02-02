{
  "Version": "2012-10-17",
  "Id": "allow_account_access_to_topic_policy",
  "Statement": [
    {
      "Sid": "allow_account_access_to_topic",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": [
        "sns:GetTopicAttributes",
        "sns:SetTopicAttributes",
        "sns:AddPermission",
        "sns:RemovePermission",
        "sns:DeleteTopic",
        "sns:Subscribe",
        "sns:ListSubscriptionsByTopic",
        "sns:Publish",
        "sns:Receive"
      ],
      "Resource": "arn:aws:sns:${region}:${account_id}:${sns_topic_name}",
      "Condition": {
        "StringEquals": {
          "AWS:SourceOwner": "${account_id}"
        }
      }
    }
  ]
}
