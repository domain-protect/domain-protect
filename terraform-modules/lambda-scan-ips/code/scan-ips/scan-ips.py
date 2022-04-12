#!/usr/bin/env python
import os
from utils.utils_aws import list_hosted_zones, list_resource_record_sets
from utils.utils_aws_ips import get_regions, get_ec2_addresses, vulnerable_aws_a_record
from utils.utils_bugcrowd import bugcrowd_create_issue
from utils.utils_db import db_get_unfixed_vulnerability_found_date_time, db_vulnerability_found
from utils.utils_db_ips import db_ip
from utils.utils_requests import get_all_aws_ec2_ips

bugcrowd = os.environ["BUGCROWD"]
env_name = os.environ["TERRAFORM_WORKSPACE"]
production_env = os.environ["PRODUCTION_WORKSPACE"]


def process_vulnerability(domain, account_name, resource_type, vulnerability_type, takeover=""):

    # check if vulnerability has already been identified
    if db_get_unfixed_vulnerability_found_date_time(domain):
        print(f"{domain} in {account_name} is still vulnerable")

    # if it's a new vulnerability, add to JSON and write to DynamoDB
    else:
        print(f"New vulnerability {domain} in {account_name}")
        vulnerable_domains.append(domain)

        if account_name == "Cloudflare":
            cloud = "Cloudflare"
        else:
            cloud = "AWS"

        if takeover:
            json_data["New"].append(
                {
                    "Account": account_name,
                    "Cloud": cloud,
                    "Domain": domain,
                    "ResourceType": resource_type,
                    "VulnerabilityType": vulnerability_type,
                    "Takeover": takeover,
                }
            )

        elif bugcrowd == "enabled" and env_name == production_env:
            bugcrowd_issue_created = bugcrowd_create_issue(domain, resource_type, vulnerability_type)

            json_data["New"].append(
                {
                    "Account": account_name,
                    "Cloud": cloud,
                    "Domain": domain,
                    "ResourceType": resource_type,
                    "VulnerabilityType": vulnerability_type,
                    "Bugcrowd": bugcrowd_issue_created,
                }
            )

        else:
            json_data["New"].append(
                {
                    "Account": account_name,
                    "Cloud": cloud,
                    "Domain": domain,
                    "ResourceType": resource_type,
                    "VulnerabilityType": vulnerability_type,
                }
            )

        db_vulnerability_found(domain, account_name, vulnerability_type, resource_type)


def a_record(account_name, record_sets, prefixes):

    record_sets_filtered = [r for r in record_sets if r["Type"] == "A" and "AliasTarget" not in r]

    for record in record_sets_filtered:
        domain = record["Name"]
        print(f"checking if {domain} is vulnerable to takeover")

        ip_addresses = [r["Value"] for r in record["ResourceRecords"]]

        for ip_address in ip_addresses:
            result = vulnerable_aws_a_record(prefixes, ip_address)

            if result:
                process_vulnerability(domain, account_name, "IP Address", "A")


def lambda_handler(event, context):  # pylint:disable=unused-argument

    global vulnerable_domains
    vulnerable_domains = []

    global json_data
    json_data = {"New": []}

    print(f"Input: {event}")

    account_id = event["Id"]
    account_name = event["Name"]
    public_ips = []
    ec2_prefixes = get_all_aws_ec2_ips()
    ip_prefixes = [i["ip_prefix"] for i in ec2_prefixes]

    print(f"Searching for new public IP addresses in {account_name} AWS account")

    regions = get_regions(account_id, account_name)

    for region in regions:
        ec2_public_ips = get_ec2_addresses(account_id, account_name, region)
        public_ips = list(set(public_ips + ec2_public_ips))

        for public_ip in public_ips:
            db_ip(public_ip, account_name, region, "EC2")

    hosted_zones = list_hosted_zones(event)

    for hosted_zone in hosted_zones:
        print(f"Searching for vulnerable A records in hosted zone {hosted_zone['Name']}")

        record_sets = list_resource_record_sets(account_id, account_name, hosted_zone["Id"])

        a_record(account_name, record_sets, ip_prefixes)
