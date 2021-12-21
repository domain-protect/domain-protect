#!/usr/bin/env python
import os, boto3
import logging
import json
import requests

from botocore.exceptions import ClientError
from datetime import datetime

from utils_aws import (list_accounts,  # pylint:disable=import-error
                       list_hosted_zones, list_resource_record_set_pages,
                       publish_to_sns)


def assume_role(account, security_audit_role_name, external_id, project, region):
    security_audit_role_arn  = "arn:aws:iam::" + account + ":role/" + security_audit_role_name

    stsclient = boto3.client('sts')

    try:
        if external_id == "":
            assumed_role_object = stsclient.assume_role(RoleArn = security_audit_role_arn, RoleSessionName = project)
            print("Assumed " + security_audit_role_name + " role in account " + account)

        else:
            assumed_role_object = stsclient.assume_role(RoleArn = security_audit_role_arn, RoleSessionName = project, ExternalId = external_id)
            print("Assumed " + security_audit_role_name + " role in account " + account)
            
    except Exception:
        logging.exception("ERROR: Failed to assume " + security_audit_role_name + " role in AWS account " + account)

    credentials = assumed_role_object['Credentials']

    aws_access_key_id     = credentials["AccessKeyId"]
    aws_secret_access_key = credentials["SecretAccessKey"]
    aws_session_token     = credentials["SessionToken"]

    boto3_session = boto3.session.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token, region_name=region)

    return boto3_session

def vulnerable_alias_cloudfront_s3(domain_name):

    try:
        response = requests.get('https://' + domain_name, timeout=1)

        if response.status_code == 404 and "Code: NoSuchBucket" in response.text:
            return "True"

        else:
            return "False"

    except:
        pass

    try:
        response = requests.get('http://' + domain_name, timeout=1)

        if response.status_code == 404 and "Code: NoSuchBucket" in response.text:
            return "True"

        else:
            return "False"

    except:
        return "False"

def lambda_handler(event, context): # pylint:disable=unused-argument
    # set variables
    region                   = os.environ['AWS_REGION']
    org_primary_account      = os.environ['ORG_PRIMARY_ACCOUNT']
    security_audit_role_name = os.environ['SECURITY_AUDIT_ROLE_NAME']
    external_id              = os.environ['EXTERNAL_ID']
    project                  = os.environ['PROJECT']

    vulnerable_domains       = []
    json_data                = {"Findings": []}

    accounts = list_accounts()

    for account in accounts:
        account_id = account['Id']
        account_name = account['Name']

        hosted_zones = list_hosted_zones(account_id, account_name)
        
        for hosted_zone in hosted_zones:
            if not hosted_zone['Config']['PrivateZone']:
                print("Searching for CloudFront alias records in hosted zone %s" % (hosted_zone['Name']) )

                pages_records = list_resource_record_set_pages(account_id, account_name, hosted_zone["Id"])
                
                for page_records in pages_records:
                    record_sets = page_records['ResourceRecordSets']
                    
                    for record in record_sets:
                        if "AliasTarget" in record:
                            if "cloudfront.net" in record['AliasTarget']['DNSName'] and "AAAA" not in record['Type']:
                                print("checking if " + record['Name'] + " is vulnerable to takeover")
                                domain_name = record['Name']
                                try:
                                    result = vulnerable_alias_cloudfront_s3(domain_name)
                                    if result == "True":
                                        print(domain_name + "in " + account_name + " is vulnerable")
                                        vulnerable_domains.append(domain_name)
                                        json_data["Findings"].append({"Account": account_name, "AccountID" : str(account_id), "Domain": domain_name})
                                except:
                                    pass
                if len(hosted_zones) == 0:
                    print("No hosted zones found in " + account_name + " account")
    
    print(json.dumps(json_data, sort_keys=True, indent=2))

    if len(vulnerable_domains) > 0:
        publish_to_sns(json_data, "Amazon Route53 Alias record for CloudFront distribution with missing S3 origin")
