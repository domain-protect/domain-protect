#!/usr/bin/env python
import os, boto3
import logging
import json
import dns.resolver

from botocore.exceptions import ClientError
from datetime import datetime

from utils_aws import (list_accounts, publish_to_sns) # pylint:disable=import-error


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

def vulnerable_ns(domain_name):

    try:
        dns.resolver.resolve(domain_name)
    except dns.resolver.NXDOMAIN:
        pass
    except dns.resolver.NoNameservers:
        try:
            ns_records = dns.resolver.resolve(domain_name, 'NS')
            if len(ns_records) > 0:
                pass
            else:
                return "True"
        except:
            return "True"
    except:
        pass

def lambda_handler(event, context): # pylint:disable=unused-argument
    # set variables
    region                   = "us-east-1"
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
        try:
            boto3_session = assume_role(account_id, security_audit_role_name, external_id, project, region)
            client = boto3_session.client('route53domains')
            try:
                paginator_domains = client.get_paginator('list_domains')
                pages_domains = paginator_domains.paginate()
                i=0
                for page_domains in pages_domains:
                    domains = page_domains['Domains']
                    #print(json.dumps(domains, sort_keys=True, indent=2, default=json_serial))
                    for domain in domains:
                        i = i + 1
                        domain_name = domain['DomainName']
                        print("testing " + domain_name + " in " + account_name + " account")
                        try:
                            result = vulnerable_ns(domain_name)
                            if result == "True":
                                print(domain_name + " in " + account_name + " is vulnerable")
                                vulnerable_domains.append(domain_name)
                                json_data["Findings"].append({"Account": account_name, "AccountID" : str(account_id), "Domain": domain_name})
                        except:
                            pass
                        
                if i == 0:
                    print("No registered domains found in " + account_name + " account")
            except:
                print("ERROR: Lambda execution role requires route53domains:ListDomains permission in " + account_name + " account")
        except:
            print("ERROR: unable to assume role in " + account_name + " account " + account_id)

    print(json.dumps(json_data, sort_keys=True, indent=2))

    if len(vulnerable_domains) > 0:
        publish_to_sns(json_data, "Registered domains with missing hosted zones found in Amazon Route53")
