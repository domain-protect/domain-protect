import json
import logging
import os

import boto3
from botocore import exceptions


def generate_role_arn(account, role_name):
    return "arn:aws:iam::" + account + ":role/" + role_name


def generate_temporary_credentials(account, role_name, external_id, project):
    security_audit_role_arn = generate_role_arn(account, role_name)

    stsclient = boto3.client("sts")

    if external_id == "":
        assumed_role_object = stsclient.assume_role(RoleArn=security_audit_role_arn, RoleSessionName=project)

    else:
        assumed_role_object = stsclient.assume_role(
            RoleArn=security_audit_role_arn,
            RoleSessionName=project,
            ExternalId=external_id,
        )

    print("Assumed " + role_name + " role in account " + account)
    return assumed_role_object


def create_session(credentials, region_override):
    region = region_override if region_override != "None" else os.environ["AWS_REGION"]

    return boto3.session.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
        region_name=region,
    )


def assume_role(account, region_override="None"):
    project = os.environ["PROJECT"]
    security_audit_role_name = os.environ["SECURITY_AUDIT_ROLE_NAME"]
    external_id = os.environ["EXTERNAL_ID"]

    try:
        assumed_role_object = generate_temporary_credentials(account, security_audit_role_name, external_id, project)

        if assumed_role_object:
            credentials = assumed_role_object["Credentials"]
        else:
            raise RuntimeError(f"could not generate STS credentials for {security_audit_role_name} role in AWS account {account}")

        return create_session(credentials, region_override)

    except Exception:
        logging.exception("ERROR: Failed to assume " + security_audit_role_name + " role in AWS account " + account)

        return None


def list_accounts():
    org_primary_account = os.environ["ORG_PRIMARY_ACCOUNT"]

    boto3_session = assume_role(org_primary_account)
    client = boto3_session.client(service_name="organizations")

    accounts_list = []

    try:
        paginator_accounts = client.get_paginator("list_accounts")
        pages_accounts = paginator_accounts.paginate()
        for page_accounts in pages_accounts:
            accounts = page_accounts["Accounts"]
            for account in accounts:
                if account["Status"] != "SUSPENDED":
                    accounts_list = accounts_list + [account]

        return accounts_list

    except Exception:
        logging.exception(
            "ERROR: Unable to list AWS accounts across organization with primary account %a",
            org_primary_account,
        )

    return []


def list_hosted_zones(route53, account):

    account_name = account["Name"]

    hosted_zones_list = []

    try:
        paginator_zones = route53.get_paginator("list_hosted_zones")
        pages_zones = paginator_zones.paginate()
        for page_zones in pages_zones:
            hosted_zones = [h for h in page_zones["HostedZones"] if not h["Config"]["PrivateZone"]]

            hosted_zones_list = hosted_zones_list + hosted_zones

        return hosted_zones_list

    except exceptions.ClientError as e:
        logging.error(
            f"ERROR: issue when listing hosted zones in {account_name} account :: [ {e} ]"
        )
        # logging.error(
        #     "ERROR: Lambda execution role requires route53:ListHostedZones permission in %a account",
        #     account_name,
        # )

    return []


def list_resource_record_sets(route53, account_name, hosted_zone_id):

    record_set_list = []

    try:
        paginator_records = route53.get_paginator("list_resource_record_sets")
        pages_records = paginator_records.paginate(
            HostedZoneId=hosted_zone_id,
            StartRecordName="_",
            StartRecordType="NS",
        )

        for page_records in pages_records:
            record_sets = page_records["ResourceRecordSets"]

            record_set_list = record_set_list + record_sets

        return record_set_list

    except Exception:
        logging.exception(
            "ERROR: Lambda execution role requires route53:ListResourceRecordSets permission in %a account",
            account_name,
        )

    return []


def list_domains(account_id, account_name):

    domain_list = []

    try:
        boto3_session = assume_role(account_id, "us-east-1")
        route53domains = boto3_session.client("route53domains")

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

    return domain_list


def publish_to_sns(json_data, subject):
    sns_topic_arn = os.environ["SNS_TOPIC_ARN"]

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


def get_cloudfront_s3_origin_url(account_id, account_name, domain):
    # returns S3 origin URL of CloudFront distribution for vulnerability detection

    try:
        boto3_session = assume_role(account_id, "us-east-1")

        try:
            cloudfront = boto3_session.client("cloudfront")
            paginator = cloudfront.get_paginator("list_distributions")
            pages = paginator.paginate()
            for page in pages:
                for distribution in page["DistributionList"]["Items"]:
                    if "Items" not in distribution["Aliases"]:
                        continue
                    for alias in distribution["Aliases"]["Items"]:
                        if alias + "." == domain:
                            # We found the right distribution
                            return distribution["Origins"]["Items"][0]["DomainName"]

        except exceptions.ClientError as e:
            print(e.response["Error"]["Code"])
            logging.error(
                "ERROR: Lambda execution role requires cloudfront:ListDistributions permission in %a account",
                account_name,
            )

    except exceptions.ClientError as e:
        print(e.response["Error"]["Code"])
        logging.error("ERROR: unable to assume role in %a account %s", account_name, account_id)

    return None


def get_cloudfront_s3_origin_takeover(account_id, account_name, domain):
    # returns S3 bucket origin of a CloudFront distribution for takeover purposes

    if domain.endswith("."):
        domain = domain[:-1]

    try:
        boto3_session = assume_role(account_id, "us-east-1")

        try:
            cloudfront = boto3_session.client("cloudfront")
            paginator_distributions = cloudfront.get_paginator("list_distributions")
            pages_distributions = paginator_distributions.paginate()

            for page_distribution in pages_distributions:
                distributions = page_distribution["DistributionList"]["Items"]
                for distribution in distributions:
                    if domain in distribution["DomainName"]:
                        s3_origin = distribution["Origins"]["Items"][0]["DomainName"]

                        return s3_origin

        except exceptions.ClientError as e:
            print(e.response["Error"]["Code"])
            logging.error(
                "ERROR: Lambda execution role requires cloudfront:ListDistributions permission in %a account",
                account_name,
            )

    except exceptions.ClientError as e:
        print(e.response["Error"]["Code"])
        logging.error("ERROR: unable to assume role in %a account %s", account_name, account_id)

    return None


def domain_deleted(domain, account_name):
    accounts = list_accounts()
    account_id = [a for a in accounts if a["Name"] == account_name][0]["Id"]

    print(f"{account_name} account has ID {account_id}")

    domains = list_domains(account_id, account_name)

    if domain in domains:
        print(f"{domain} still in Route53 registered domains")
        return False

    print(f"{domain} no longer in Route53 registered domains")

    return True


def eb_susceptible(domain):
    """Returns a value of True if the domain is susceptible to EB hijacking"""
    # remove trailing dot if present
    if domain.endswith("."):
        domain = domain[:-1]

    # identify if Elastic Beanstalk name has been auto created by AWS
    if domain.endswith(".elasticbeanstalk.com"):
        if len(domain.split(".")) == 5:
            print(f"ignoring {domain} as auto-generated by AWS so not susceptible to takeover")
            return False

        # don't include Elastic Beanstalk domains starting eba- as this prefix is reserved by AWS
        if domain.startswith("eba-"):
            print(f"ignoring {domain} as prefix eba- is reserved by AWS so not susceptible to takeover")
            return False

        # the Elastic Beanstalk is vulnerable to hijacking if neither of the above conditions are met
        return True

    # domain is not an Elastic Beanstalk domain
    return False
