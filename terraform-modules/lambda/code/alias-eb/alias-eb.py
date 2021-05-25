#!/usr/bin/env python
import os, boto3
import logging
import json
import dns.resolver

from botocore.exceptions import ClientError
from datetime import datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")

def assume_role(account, security_audit_role_name, external_id, project, region):
    security_audit_role_arn  = "arn:aws:iam::" + account + ":role/" + security_audit_role_name

    stsclient = boto3.client('sts')

    try:
        if external_id == "":
            assumed_role_object = stsclient.assume_role(RoleArn = security_audit_role_arn, RoleSessionName = project)

        else:
            assumed_role_object = stsclient.assume_role(RoleArn = security_audit_role_arn, RoleSessionName = project, ExternalId = external_id)

    except Exception:
        logging.exception("ERROR: Failed to assume " + security_audit_role_name + " role in AWS account " + account)

    print("Assumed " + security_audit_role_name + " role in account " + account)

    credentials = assumed_role_object['Credentials']

    aws_access_key_id     = credentials["AccessKeyId"]
    aws_secret_access_key = credentials["SecretAccessKey"]
    aws_session_token     = credentials["SessionToken"]

    boto3_session = boto3.session.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token, region_name=region)

    return boto3_session

def vulnerable_alias_eb(domain_name):

    try:
        dns.resolver.resolve(domain_name, 'A')
        return "False"
    except dns.resolver.NoAnswer:
        return "True"
    except:
        return "False"

def lambda_handler(event, context):
    # set variables
    region                   = os.environ['AWS_REGION']
    org_primary_account      = os.environ['ORG_PRIMARY_ACCOUNT']
    security_audit_role_name = os.environ['SECURITY_AUDIT_ROLE_NAME']
    external_id              = os.environ['EXTERNAL_ID']
    project                  = os.environ['PROJECT']
    sns_topic_arn            = os.environ['SNS_TOPIC_ARN']

    vulnerable_domains       = []
    json_data                = {"Findings": []}

    boto3_session = assume_role(org_primary_account, security_audit_role_name, external_id, project, region)

    client = boto3_session.client(service_name = "organizations")

    try:
        accounts = client.list_accounts()['Accounts']
        for account in accounts:
            account_id = account['Id']
            account_name = account['Name']
            try:
                boto3_session = assume_role(account_id, security_audit_role_name, external_id, project, region)
                client = boto3_session.client('route53')
                try:
                    hosted_zones = client.list_hosted_zones()['HostedZones']
                    #print(json.dumps(hosted_zones, sort_keys=True, indent=2, default=json_serial))

                    for hosted_zone in hosted_zones:
                        if not hosted_zone['Config']['PrivateZone']:
                            print("Searching for Elastic Beanstalk alias records in hosted zone %s" % (hosted_zone['Name']) )
                            try:
                                record_sets = client.list_resource_record_sets(HostedZoneId=hosted_zone['Id'], StartRecordName='_', StartRecordType='A')
                                #print(json.dumps(record_sets, sort_keys=True, indent=2, default=json_serial))
                                i=0
                                for record in record_sets['ResourceRecordSets']:
                                    if "AliasTarget" in record:
                                        if (record['AliasTarget']['DNSName']).endswith('elasticbeanstalk.com.'):
                                            print("checking if " + record['Name'] + " is vulnerable to takeover")
                                            i = i + 1
                                            domain_name = record['Name']
                                            try:
                                                result = vulnerable_alias_eb(domain_name)
                                                if result == "True":
                                                    print(domain_name + "in " + account_name + " is vulnerable")
                                                    vulnerable_domains.append(domain_name)
                                                    json_data["Findings"].append({"Account": account_name, "AccountID" : str(account_id), "Domain": domain_name})

                                            except:
                                                pass
                            except:
                                pass
                except:
                    pass

            except:
                print("ERROR: unable to assume role in account " + account_id)

    except Exception:
        logging.exception("ERROR: Unable to list AWS accounts across organization with primary account " + org_primary_account)

    try:
        print(json.dumps(json_data, sort_keys=True, indent=2, default=json_serial))
        #print(json_data)
        client = boto3.client('sns')

        if len(vulnerable_domains) > 0:
            response = client.publish(
                TargetArn=sns_topic_arn,
                Subject="Vulnerable Elastic Beanstalk alias records found in Amazon Route53",
                Message=json.dumps({'default': json.dumps(json_data)}),
                MessageStructure='json'
            )
            print(response)

    except:
        logging.exception("ERROR: Unable to publish to SNS topic " + sns_topic_arn)
