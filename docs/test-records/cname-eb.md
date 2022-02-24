# Alias Elastic Beanstalk
* Amazon Route53, hosted zone
* Create a CNAME pointing to a missing Elastic Beanstalk environment as detailed [here](cname-eb.md)
* wait for an Elastic Beanstalk environment to be created by automatic takeover
* delete the CNAME record
* create an alias record as shown below
* delete the Elastic Beanstalk environment by deleting its CloudFormation template in the same region

![Alt text](images/alias-eb.png?raw=true "Example DNS record")

* remove the DNS record and takeover Elastic Beanstalk environment as soon as possible to minimise costs

[Back to Tests](..\tests.md)
