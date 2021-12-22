import json
import logging
import os

import boto3

org_primary_account = os.environ["ORG_PRIMARY_ACCOUNT"]
security_audit_role_name = os.environ["SECURITY_AUDIT_ROLE_NAME"]
external_id = os.environ["EXTERNAL_ID"]
sns_topic_arn = os.environ["SNS_TOPIC_ARN"]
project = os.environ["PROJECT"]


def assume_role(account, region_override="None"):
    security_audit_role_arn = "arn:aws:iam::" + account + ":role/" + security_audit_role_name

    stsclient = boto3.client("sts")

    try:
        if external_id == "":
            assumed_role_object = stsclient.assume_role(RoleArn=security_audit_role_arn, RoleSessionName=project)
            print("Assumed " + security_audit_role_name + " role in account " + account)

        else:
            assumed_role_object = stsclient.assume_role(
                RoleArn=security_audit_role_arn, RoleSessionName=project, ExternalId=external_id
            )
            print("Assumed " + security_audit_role_name + " role in account " + account)

    except Exception:
        logging.exception("ERROR: Failed to assume " + security_audit_role_name + " role in AWS account " + account)

    credentials = assumed_role_object["Credentials"]

    aws_access_key_id = credentials["AccessKeyId"]
    aws_secret_access_key = credentials["SecretAccessKey"]
    aws_session_token = credentials["SessionToken"]

    if region_override != "None":
        region = region_override

    else:
        region = os.environ["AWS_REGION"]

    boto3_session = boto3.session.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        region_name=region,
    )

    return boto3_session


def list_accounts():
    boto3_session = assume_role(org_primary_account)

    client = boto3_session.client(service_name="organizations")

    try:
        paginator_accounts = client.get_paginator("list_accounts")
        pages_accounts = paginator_accounts.paginate()
        for page_accounts in pages_accounts:
            accounts = page_accounts["Accounts"]

        return accounts

    except Exception:
        logging.exception(
            "ERROR: Unable to list AWS accounts across organization with primary account %a", org_primary_account
        )

    return []


def list_hosted_zones(account_id, account_name):

    try:
        boto3_session = assume_role(account_id)
        route53 = boto3_session.client("route53")

        hosted_zones_list = []

        try:
            paginator_zones = route53.get_paginator("list_hosted_zones")
            pages_zones = paginator_zones.paginate()
            for page_zones in pages_zones:
                hosted_zones = [h for h in page_zones["HostedZones"] if not h["Config"]["PrivateZone"]]

                hosted_zones_list = hosted_zones_list + hosted_zones

            return hosted_zones_list

        except Exception:
            logging.error(
                "ERROR: Lambda execution role requires route53:ListHostedZones permission in %a account", account_name
            )

    except Exception:
        logging.error("ERROR: unable to assume role in %a account %s", account_name, account_id)

    return []


def list_resource_record_set_pages(account_id, account_name, hosted_zone_id):

    try:
        boto3_session = assume_role(account_id)
        route53 = boto3_session.client("route53")

        try:
            paginator_records = route53.get_paginator("list_resource_record_sets")
            pages_records = paginator_records.paginate(
                HostedZoneId=hosted_zone_id, StartRecordName="_", StartRecordType="NS"
            )

            return pages_records

        except Exception:
            logging.exception(
                "ERROR: Lambda execution role requires route53:ListResourceRecordSets permission in %a account",
                account_name,
            )

    except Exception:
        logging.error("ERROR: unable to assume role in %a account %s", account_name, account_id)

    return []


def list_domains(account_id, account_name):

    try:
        boto3_session = assume_role(account_id, "us-east-1")
        route53domains = boto3_session.client("route53domains")

        domain_list = []

        try:
            paginator_domains = route53domains.get_paginator("list_domains")
            pages_domains = paginator_domains.paginate()

            for page_domains in pages_domains:
                domains = page_domains["Domains"]
                for domain in domains:
                    domain_name = domain["DomainName"]
                    domain_list.append(domain_name)

            return domain_list

        except Exception:
            logging.error(
                "ERROR: Lambda execution role requires route53domains:ListDomains permission in %a account",
                account_name,
            )

    except Exception:
        logging.error("ERROR: unable to assume role in %a account %s", account_name, account_id)

    return []


def publish_to_sns(json_data, subject):

    try:
        print(json.dumps(json_data, sort_keys=True, indent=2))
        client = boto3.client("sns")

        response = client.publish(
            TargetArn=sns_topic_arn,
            Subject=subject,
            Message=json.dumps({"default": json.dumps(json_data)}),
            MessageStructure="json",
        )
        print(response)

    except Exception:
        logging.exception("ERROR: Unable to publish to SNS topic %s", sns_topic_arn)
