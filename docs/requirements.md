# Requirements

* Security audit account within AWS Organizations
* Security audit read-only role with an identical name in every AWS account of the Organization
* Storage bucket for Terraform state file

## Requirements for takeover
* Creation of takeover resources in security account must not be blocked in some regions by SCP
* S3 Block Public Access must not be turned on at the account level in the security account
* Production workspace must be named `prd` or set to an alternate using a Terraform variable
* See [automated takeover](automated-takeover.md) for further details

## Organisations with over 1,000 AWS accounts
* A separate scanning Lambda function is started for every AWS account in the organisation
* If you have over 1,000 AWS accounts, request an increase to the Lambda default concurrent execution limit

[back to README](../README.md)