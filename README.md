# domain-protect

* scans AWS Route53 for ElasticBeanstalk CNAMES vulnerable to takeover
* scans AWS Route53 for subdomain NS delegations vulnerable to takeover

## requirements
* Python 3.x
```
pip install boto3
pip install dnspython
```

## usage - ElasticBeanstalk CNAMES
* replace PROFILE_NAME by your AWS CLI profile name
```
python aws-cname-eb-protect.py --profile PROFILE_NAME
```

![Alt text](vulnerable-eb-cnames.png?raw=true "Detect vulnerable ElasticBeanstalk CNAMEs")

## usage - subdomain NS delegations
* replace PROFILE_NAME by your AWS CLI profile name
```
python aws-ns-detect.py --profile PROFILE_NAME
```

![Alt text](vulnerable-ns.png?raw=true "Detect vulnerable subdomains")

## usage - assume role from another AWS account
* log in to the AWS console in the audit account
* start CloudShell in a region which supports it, e.g. eu-west-1
* clone this GitHub repository, or upload relevant files from your desktop  
* edit the example below with the AWS account number of the target account, the role name, and the role session name
```
aws sts assume-role --role-arn arn:aws:iam::012345678901:role/securityaudit --role-session-name domainprotect
```
* copy and paste the returned temporary credentials to your desktop
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
* NS subdomain takeover detection from [NSDetect](https://github.com/shivsahni/NSDetect)