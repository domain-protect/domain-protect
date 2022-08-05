#!/usr/bin/env python
import os
import json
from utils.utils_aws import list_hosted_zones, list_resource_record_sets, publish_to_sns
from utils.utils_aws_ips import (
    get_regions,
    get_eip_addresses,
    get_ec2_addresses,
    get_ecs_addresses,
    vulnerable_aws_a_record,
    get_accelerator_addresses,
)
from utils.utils_bugcrowd import bugcrowd_create_issue
from utils.utils_db import db_get_unfixed_vulnerability_found_date_time, db_vulnerability_found
from utils.utils_db_ips import db_ip, db_get_ip_table_name, db_count_items
from utils.utils_requests import get_all_aws_ips
from utils.utils_sanitise import sanitise_wildcards, restore_wildcard

bugcrowd = os.environ["BUGCROWD"]
env_name = os.environ["TERRAFORM_WORKSPACE"]
production_env = os.environ["PRODUCTION_WORKSPACE"]
ip_time_limit = os.environ["IP_TIME_LIMIT"]


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
        domain = restore_wildcard(domain)
        print(f"checking if {domain} is vulnerable to takeover")

        ip_addresses = [r["Value"] for r in record["ResourceRecords"]]

        for ip_address in ip_addresses:
            result = vulnerable_aws_a_record(prefixes, ip_address, ip_time_limit)

            if result:
                process_vulnerability(domain, account_name, ip_address, "A")


def get_ips(account_id, account_name):

    accelerator_ips = get_accelerator_addresses(account_id, account_name)

    for accelerator_ip in accelerator_ips:
        db_ip(accelerator_ip, account_name, "global", "Global Accelerator IP")

    regions = get_regions(account_id, account_name)

    for region in regions:
        ec2_eips = get_eip_addresses(account_id, account_name, region)

        for ec2_eip in ec2_eips:
            db_ip(ec2_eip, account_name, region, "EC2 Elastic IP")

        ec2_public_ips = get_ec2_addresses(account_id, account_name, region)

        for ec2_public_ip in ec2_public_ips:
            db_ip(ec2_public_ip, account_name, region, "EC2 Public IP")

        ecs_public_ips = get_ecs_addresses(account_id, account_name, region)

        for ecs_public_ip in ecs_public_ips:
            db_ip(ecs_public_ip, account_name, region, "ECS Public IP")


def lambda_handler(event, context):  # pylint:disable=unused-argument

    global vulnerable_domains
    vulnerable_domains = []

    global json_data
    json_data = {"New": []}

    print(f"Input: {event}")

    account_id = event["Id"]
    account_name = event["Name"]
    prefixes = get_all_aws_ips()
    ip_prefixes = [i["ip_prefix"] for i in prefixes]
    item_count = db_count_items(db_get_ip_table_name())

    print(f"{item_count} IP addresses currently in database")
    print(f"Searching for new public IP addresses in {account_name} AWS account")

    get_ips(account_id, account_name)

    hosted_zones = list_hosted_zones(event)

    if item_count > 0:  # don't test for vulnerabilities until DynamoDB table is populated across organisation
        for hosted_zone in hosted_zones:
            print(f"Searching for vulnerable A records in hosted zone {hosted_zone['Name']}")

            record_sets = list_resource_record_sets(account_id, account_name, hosted_zone["Id"])
            record_sets = sanitise_wildcards(record_sets)

            a_record(account_name, record_sets, ip_prefixes)

        print(json.dumps(json_data, sort_keys=True, indent=2))

        if len(vulnerable_domains) > 0:
            publish_to_sns(json_data, "New domains vulnerable to takeover")

    else:
        print(f"skipping vulnerability check until {db_get_ip_table_name()} database table is populated")
