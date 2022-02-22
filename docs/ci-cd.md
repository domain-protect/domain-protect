## CI/CD

* infrastructure has been deployed using CircleCI
* environment variables to be entered in CircleCI project settings:

| ENVIRONMENT VARIABLE            | EXAMPLE VALUE / COMMENT                          |
| ------------------------------- | -------------------------------------------------|
| AWS_ACCESS_KEY_ID               | using [domain-protect deploy policy](aws-iam-policies/domain-protect-deploy.json)|
| AWS_SECRET_ACCESS_KEY           | -                                                |
| TERRAFORM_STATE_BUCKET          | tfstate48903                                     |
| TERRAFORM_STATE_KEY             | domain-protect                                   |
| TERRAFORM_STATE_REGION          | us-east-1                                        |  
| TF_VAR_org_primary_account      | 012345678901                                     | 
| TF_VAR_security_audit_role_name | not needed if "domain-protect-audit" used        |
| TF_VAR_external_id              | only required if External ID is configured       |
| TF_VAR_slack_channels           | ["security-alerts"]                              |
| TF_VAR_slack_channels_dev       | ["security-alerts-dev"]                          |
| TF_VAR_slack_webhook_urls       | ["https://hooks.slack.com/services/XXX/XXX/XXX"] | 

## Validation of updated CircleCI configuration:
```
docker run -v `pwd`:/whatever circleci/circleci-cli circleci config validate /whatever/.circleci/config.yml
```