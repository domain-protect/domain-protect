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

## acknowledgement
* NS subdomain takeover detection from [NSDetect](https://github.com/shivsahni/NSDetect)