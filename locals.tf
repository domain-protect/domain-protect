locals {
  env = lower(terraform.workspace)
}

# to add extra elements to the lists below, define the additional variables for additional Slack channels and add below
# this is a workaround to overcome limitations in CircleCI preventing list variables being defined
locals {
  slack_channels     = tolist([var.slack_channel])
  slack_channels_dev = tolist([var.slack_channel_dev])
  slack_webhook_urls = tolist([var.slack_webhook_url])
}