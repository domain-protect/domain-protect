# domain-protect manual scans

* scans AWS Route53 for ElasticBeanstalk Alias records vulnerable to takeover
* scans AWS Route53 for ElasticBeanstalk CNAMES vulnerable to takeover
* scans AWS Route53 for S3 Alias records vulnerable to takeover
* scans AWS Route53 for S3 CNAMES vulnerable to takeover  
* scans AWS Route53 for subdomain NS delegations vulnerable to takeover

## requirements
* Python 3.x
```
pip install boto3
pip install dnspython
pip install requests
```
## usage - CloudFront Alias with missing S3 origin
* replace PROFILE_NAME by your AWS CLI profile name
```
python aws-alias-cloudfront-s3.py --profile PROFILE_NAME
```

![Alt text](images/aws-cloudfront-s3-alias.png?raw=true "CloudFront Alias with missing S3 origin")

## usage - CloudFront CNAME with missing S3 origin
* replace PROFILE_NAME by your AWS CLI profile name
```
python aws-cname-cloudfront-s3.py --profile PROFILE_NAME
```

![Alt text](images/aws-cloudfront-s3-cname.png?raw=true "CloudFront CNAME with missing S3 origin")

## usage - ElasticBeanstalk Alias
* replace PROFILE_NAME by your AWS CLI profile name
```
python aws-alias-eb.py --profile PROFILE_NAME
```

![Alt text](images/aws-eb-alias.png?raw=true "Detect vulnerable S3 Aliases")

## usage - ElasticBeanstalk CNAMES
* replace PROFILE_NAME by your AWS CLI profile name
```
python aws-cname-eb.py --profile PROFILE_NAME
```

![Alt text](images/aws-eb-cnames.png?raw=true "Detect vulnerable ElasticBeanstalk CNAMEs")

## usage - S3 Alias
* replace PROFILE_NAME by your AWS CLI profile name
```
python aws-alias-s3.py --profile PROFILE_NAME
```

![Alt text](images/aws-s3-alias.png?raw=true "Detect vulnerable S3 Aliases")

## usage - S3 CNAMES
* replace PROFILE_NAME by your AWS CLI profile name
```
python aws-cname-s3.py --profile PROFILE_NAME
```

![Alt text](images/aws-s3-cnames.png?raw=true "Detect vulnerable S3 CNAMEs")

## usage - subdomain NS delegations
* replace PROFILE_NAME by your AWS CLI profile name
```
python aws-ns.py --profile PROFILE_NAME
```

![Alt text](images/aws-ns.png?raw=true "Detect vulnerable subdomains")

## usage - assume role from another AWS account
* log in to the AWS console in the audit account
* start CloudShell in a region which supports it, e.g. eu-west-1
* upload relevant files from your desktop  
* edit the example below with the AWS account number of the target account, the role name, and the role session name
```
aws sts assume-role --role-arn arn:aws:iam::012345678901:role/securityaudit --role-session-name domainprotect
```
* copy and paste the returned temporary credentials to your desktop
* create AWS cli credentials in CloudShell
```
vi .aws/credentials
```
* enter details in the following format
```
[profile_name]
aws_access_key_id = XXXXXXXXXXXXXXXXXXXXXX
aws_secret_access_key = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
aws_session_token = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```
* save and exit vi
```
:wq!
```
* install dependencies and proceed with the scans, e.g. 
```
sudo pip3 install dnspython
python3 aws-ns.py --profile profile_name
```

## acknowledgement
* NS subdomain takeover detection based on [NSDetect](https://github.com/shivsahni/NSDetect)