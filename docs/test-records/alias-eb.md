# Alias Elastic Beanstalk
* in the same AWS account as the Route53 hosted zone, create an Elastic Beanstalk environment
* use [content.zip](../../terraform-modules/lambda-takeover/code/takeover/eb-content/content.zip) from this repository
* if testing detection only, the Elastic Beanstalk environment can be created via the console
* for testing takeover and detection, create the environment using CloudFormation or Terraform
* this is because AWS uses a different CNAME syntax when creating via the console
* CNAME syntax for console created Elastic Beanstalk environments is not vulnerable to takeover
* after the Elastic Beanstalk environment has deployed, create the Alias record in Route53

![Alt text](images/alias-eb.png?raw=true "DNS Record")

* delete the Elastic Beanstalk environment
* remove the DNS record and takeover Elastic Beanstalk environment as soon as possible to minimise costs

[Back to Manual Tests](../manual-tests.md)
