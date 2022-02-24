# Alerts and reports
<kbd>
  <img src="images/new.png" width="600">
</kbd>

<kbd>
  <img src="images/slack-ns.png" width="500">
</kbd>

<kbd>
  <img src="images/fixed.png" width="400">
</kbd>

<kbd>
  <img src="images/takeover-notification.png" width="500">
</kbd>

<kbd>
  <img src="images/resources-notification.png" width="500">
</kbd>

|Information                  |Notification type|Default schedule |
|-----------------------------|-----------------|-----------------|
|New vulnerability            |alert            |60 minutes       |
|Current vulnerabilities      |report           |24 hours         |
|Fixed vulnerability          |alert            |60 minutes       |
|Takeover status              |alert            |immediate        |
|Resources preventing takeover|report           |24 hours         |


## notification channels
* Slack via lambda function subscribed to SNS topic
* Email in JSON format by directly subscribing to SNS topic

## Slack channel for non-prod environments
* Specify different Slack channel for non-prod environment
* Avoids duplication in your main security Slack channel

## add notifications to extra Slack channels
* add an extra channel to your slack_channels variable list
* add an extra webhook URL or repeat the same webhook URL to your slack_webhook_urls variable list
* apply Terraform

## customise notification schedules
* update the relevant Terraform variable in your pipeline or tfvars file
* apply Terraform

[back to README](../README.md)