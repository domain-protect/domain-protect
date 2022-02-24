# CNAME CloudFront
* Deploy [aws-cloudfront](https://github.com/celidor/aws-cloudfront) using Terraform
* This will create resources in CloudFront, S3, Certificate Manager and Route53
* Route53 record is a CNAME pointing to the CloudFront distrubtion
* Delete the origin S3 bucket manually using the console

![Alt text](images/cname-cloudfront.png?raw=true "CloudFront Distribution")

[Back to Tests](..\tests.md)
