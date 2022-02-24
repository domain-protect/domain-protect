# Alias Elastic Beanstalk
* In the same AWS account as the Route53 hosted zone, create an Elastic Beanstalk environment using a CloudFormation template
* use content.zip from [this repository](https://github.com/ovotech/domain-protect/blob/dev/terraform-modules/lambda-takeover/code/takeover/eb-content/content.zip)
* create the Alias record in Route53

![Alt text](images/alias-eb.png?raw=true "DNS Record")

* delete the Elastic Beanstalk environment
* remove the DNS record and takeover Elastic Beanstalk environment as soon as possible to minimise costs

[Back to Tests](..\tests.md)
