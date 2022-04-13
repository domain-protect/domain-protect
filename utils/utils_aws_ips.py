import os
import logging
import ipaddress
from botocore import exceptions
from utils.utils_aws import assume_role
from utils.utils_db_ips import db_check_ip

allowed_regions = os.environ["ALLOWED_REGIONS"][1:][:-1]
allowed_regions = allowed_regions.replace(" ", "")
allowed_regions = allowed_regions.replace("'", "")
allowed_regions = allowed_regions.split(",")


def get_all_regions(account_id, account_name):
    # get regions within each account in case extra regions are enabled

    try:
        boto3_session = assume_role(account_id)

        try:
            ec2 = boto3_session.client("ec2")

            response = ec2.describe_regions()
            return [region["RegionName"] for region in response["Regions"]]

        except exceptions.ClientError as e:
            print(e.response["Error"]["Code"])
            logging.error(
                "ERROR: Lambda execution role requires ec2:DescribeRegions permission in %a account",
                account_name,
            )

    except exceptions.ClientError as e:
        print(e.response["Error"]["Code"])
        logging.error("ERROR: unable to assume role in %a account %s", account_name, account_id)

    return []


def get_regions(account_id, account_name):

    if allowed_regions != ["all"]:
        regions = allowed_regions

    else:
        regions = get_all_regions(account_id, account_name)

    return regions


def get_eip_addresses(account_id, account_name, region):
    # get EC2 elastic IP addresses

    ec2_elastic_ips = []

    try:
        boto3_session = assume_role(account_id, region)

        try:
            ec2 = boto3_session.client("ec2")
            response = ec2.describe_addresses()
            addresses = response["Addresses"]

            for address in addresses:
                try:
                    ec2_elastic_ip = address["PublicIp"]
                    ec2_elastic_ips.append(ec2_elastic_ip)

                except KeyError:
                    pass

        except exceptions.ClientError as e:
            print(e.response["Error"]["Code"])
            logging.error(
                "ERROR: Lambda role requires ec2:DescribeAddresses permission in %r for %a account",
                region,
                account_name,
            )

    except exceptions.ClientError as e:
        print(e.response["Error"]["Code"])
        logging.error("ERROR: unable to assume role in %r for %a account", region, account_name)

    return ec2_elastic_ips


def vulnerable_aws_a_record(ip_prefixes, ip_address):

    if ipaddress.ip_address(ip_address).is_private:
        return False

    if db_check_ip(ip_address, 48):  # check if IP address is in database and seen in last 48 hours
        return False

    for ip_prefix in ip_prefixes:
        if ipaddress.ip_address(ip_address) in ipaddress.ip_network(ip_prefix):
            return True

    return False
