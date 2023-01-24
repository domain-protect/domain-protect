# Requirements

In order to deploy resources from this repo successfully, it is necessary to meet the requirements below, as the terraform code we provide will not create them

* Slack App or legacy Slack webhook, see [Slack Webhook](slack-webhook.md) for details
* Security audit account within AWS Organizations
* Security audit read-only role with an identical name in every AWS account of the Organization
* Storage bucket for Terraform state file
* OIDC role (preferred) or IAM user with [deploy policy](../aws-iam-policies/domain-protect-deploy.json) assigned, for CI/CD deployment

## Security audit role in every AWS account

* You may already have an existing security audit role in all your AWS accounts
* You can select using the `security_audit_role_name` Terraform variable
* If you don't already have a suitable role in all AWS accounts, create a new one
* Name new role `domain-protect-audit` to match default Terraform variable value
* Assign [domain-protect-audit](../aws-iam-policies/domain-protect-audit.json) IAM policy
* Set [trust policy](../aws-iam-policies/domain-protect-audit-trust-external-id.json) with Security Audit AWS Account ID
* Use External ID in trust policy
* Deploy across  Organization using [CloudFormation StackSets](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/what-is-cfnstacksets.html)

## Requirements for takeover

* Creation of takeover resources in security account must not be blocked in some regions by SCP
* S3 Block Public Access must not be turned on at the account level in the security account
* Production workspace must be named `prd` or set to an alternate using a Terraform variable
* See [automated takeover](automated-takeover.md) for further details

## Organisations with over 1,000 AWS accounts

* A separate scanning Lambda function is started for every AWS account in the organisation
* If you have over 1,000 AWS accounts, request an increase to the Lambda default concurrent execution limit

[back to README](../README.md)