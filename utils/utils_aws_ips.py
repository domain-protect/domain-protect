import logging
from botocore import exceptions
from utils.utils_aws import assume_role


def get_regions(account_id, account_name):
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


def get_ec2_addresses(account_id, account_name, region):
    # get EC2 public IP addresses

    ec2_public_ips = []

    try:
        boto3_session = assume_role(account_id, region)

        try:
            ec2 = boto3_session.client("ec2")
            response = ec2.describe_addresses()
            addresses = response["Addresses"]

            for address in addresses:
                try:
                    ec2_public_ip = address["PublicIp"]
                    ec2_public_ips.append(ec2_public_ip)

                except KeyError:
                    pass

        except exceptions.ClientError as e:
            print(e.response["Error"]["Code"])
            logging.error("ERROR: Lambda role requires ec2:DescribeAddresses permission in %r for %a account")

    except exceptions.ClientError as e:
        print(e.response["Error"]["Code"])
        logging.error("ERROR: unable to assume role in %r for %a account", region, account_name)

    return ec2_public_ips
