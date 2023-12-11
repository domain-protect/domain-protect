#!/usr/bin/env python
import argparse

import boto3
import requests

from utils.utils_aws_manual import list_hosted_zones_manual_scan
from utils.utils_print import my_print
from utils.utils_print import print_list


def vulnerable_alias_s3(domain_name):

    try:
        response = requests.get("http://" + domain_name, timeout=1)

        if response.status_code == 404 and "Code: NoSuchBucket" in response.text:
            return True

    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        pass

    return False


def route53():
    vulnerable_domains = []
    missing_resources = []

    print("Searching for Route53 hosted zones")

    session = boto3.Session()
    route53 = session.client("route53")

    hosted_zones = list_hosted_zones_manual_scan()
    for hosted_zone in hosted_zones:
        print(f"Searching for S3 Alias records in hosted zone {hosted_zone['Name']}")

        paginator_records = route53.get_paginator("list_resource_record_sets")
        pages_records = paginator_records.paginate(
            HostedZoneId=hosted_zone["Id"],
            StartRecordName="_",
            StartRecordType="NS",
        )
        i = 0
        for page_records in pages_records:
            record_sets = [
                r
                for r in page_records["ResourceRecordSets"]
                if "AliasTarget" in r
                if ("amazonaws.com" in r["AliasTarget"]["DNSName"]) and "s3-website" in (r["AliasTarget"]["DNSName"])
            ]
            for record in record_sets:
                i = i + 1
                result = vulnerable_alias_s3(record["Name"])
                if result:
                    vulnerable_domains.append(record["Name"])
                    my_print(f"{str(i)}. {record['Name']}", "ERROR")
                    missing_resources.append(record["Name"] + record["AliasTarget"]["DNSName"])
                else:
                    my_print(f"{str(i)}. {record['Name']}", "SECURE")

    return (vulnerable_domains, missing_resources)


def main():
    parser = argparse.ArgumentParser(description="Prevent Subdomain Takeover")
    args = parser.parse_args()

    vulnerable_domains, missing_resources = route53()

    count = len(vulnerable_domains)
    my_print(f"\nTotal Vulnerable Domains Found: {str(count)}", "INFOB")

    if count > 0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains, "INSECURE_WS")

        my_print("\nCreate these resources to prevent takeover: ", "INFOB")
        print_list(missing_resources, "OUTPUT_WS")


if __name__ == "__main__":
    main()
