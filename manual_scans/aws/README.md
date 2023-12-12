# domain-protect manual scans
scans Amazon Route53 to detect:
* Alias records for CloudFront distributions with missing S3 origin
* CNAME records for CloudFront distributions with missing S3 origin
* ElasticBeanstalk Alias records vulnerable to takeover
* ElasticBeanstalk CNAMES vulnerable to takeover
* S3 Alias records vulnerable to takeover
* S3 CNAMES vulnerable to takeover
* Registered domains with missing hosted zones
* Subdomain NS delegations vulnerable to takeover

## Python setup
* optionally create and activate a virtual environment
```
python -m venv .venv
source .venv/bin/activate
```
* install dependencies
```
pip install -r manual_scans/aws/requirements.txt
```
* set PYTHONPATH to import modules
* identify your current path from the root of the domain-protect directory
```
$ pwd
/Users/paul/src/github.com/ovotech/domain-protect
```
* set PYTHONPATH environment variable
```
$ export PYTHONPATH="${PYTHONPATH}:/Users/paul/src/github.com/domain-protect/domain-protect"
```
* run manual scans from root of domain-protect folder

## CloudFront Alias with missing S3 origin


```
python manual_scans/aws/aws-alias-cloudfront-s3.py
```

![Alt text](images/aws-cloudfront-s3-alias.png?raw=true "CloudFront Alias with missing S3 origin")

## CloudFront CNAME with missing S3 origin

```
python manual_scans/aws/aws-cname-cloudfront-s3.py
```

![Alt text](images/aws-cloudfront-s3-cname.png?raw=true "CloudFront CNAME with missing S3 origin")

## ElasticBeanstalk Alias

```
python manual_scans/aws/aws-alias-eb.py
```

![Alt text](images/aws-eb-alias.png?raw=true "Detect vulnerable S3 Aliases")

## ElasticBeanstalk CNAMES

```
python manual_scans/aws/aws-cname-eb.py
```

![Alt text](images/aws-eb-cnames.png?raw=true "Detect vulnerable ElasticBeanstalk CNAMEs")

## S3 Alias

```
python manual_scans/aws/aws_alias_s3.py
```

![Alt text](images/aws-s3-alias.png?raw=true "Detect vulnerable S3 Aliases")

## S3 CNAMES

```
python manual_scans/aws/aws-cname-s3.py
```

![Alt text](images/aws-s3-cnames.png?raw=true "Detect vulnerable S3 CNAMEs")

## registered domains with missing hosted zone

```
python manual_scans/aws/aws-ns-domain.py
```

![Alt text](images/aws-ns-domain.png?raw=true "Detect vulnerable subdomains")

## subdomain NS delegations

```
python manual_scans/aws/aws-ns-subdomain.py
```

![Alt text](images/aws-ns-subdomain.png?raw=true "Detect vulnerable subdomains")

## assume role from another AWS account
* log in to the AWS console in the audit account
* start CloudShell in a region which supports it, e.g. eu-west-1
* upload relevant files from your desktop
* edit the example below with the AWS account number of the target account, the role name, and the role session name
```
aws sts assume-role --role-arn arn:aws:iam::012345678901:role/securityaudit --role-session-name domainprotect
```
* set the returned temporary credentials in the environmebt variables of your local machine:

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...
```

* install dependencies and proceed with the scans, e.g.
```
sudo pip3 install dnspython
python3 manual_scans/aws/aws-ns-domain.py
```

[back to README](../../README.md)

## acknowledgement
* NS subdomain takeover detection based on [NSDetect](https://github.com/shivsahni/NSDetect)
