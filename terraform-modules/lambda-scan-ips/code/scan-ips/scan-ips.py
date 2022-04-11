#!/usr/bin/env python
import os
from utils.utils_aws_ips import get_regions, get_ec2_addresses

allowed_regions = os.environ["ALLOWED_REGIONS"][1:][:-1]
allowed_regions = allowed_regions.replace(" ", "")
allowed_regions = allowed_regions.replace("'", "")
allowed_regions = allowed_regions.split(",")


def lambda_handler(event, context):  # pylint:disable=unused-argument

    print(f"Input: {event}")

    account_id = event["Id"]
    account_name = event["Name"]

    print(f"Searching for EC2 public IP addresses in {account_name} AWS account")

    if allowed_regions != ["all"]:
        regions = allowed_regions

    else:
        regions = get_regions(account_id, account_name)

    for region in regions:
        ec2_public_ips = get_ec2_addresses(account_id, account_name, region)
        print(f"Public IPs in {region}: {ec2_public_ips}")
