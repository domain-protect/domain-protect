#!/usr/bin/env python
import argparse

import boto3

from utils.aws import list_hosted_zones_manual_scan
from utils.dns import vulnerable_ns
from utils.print import my_print, print_list

vulnerable_domains = []


def route53(profile):

    session = boto3.Session(profile_name=profile)
    route53 = session.client("route53")

    print("Searching for Route53 hosted zones")
    hosted_zones = list_hosted_zones_manual_scan(profile)
    for hosted_zone in hosted_zones:
        print(f"Searching for subdomain NS records in hosted zone {hosted_zone['Name']}")
        paginator_records = route53.get_paginator("list_resource_record_sets")
        pages_records = paginator_records.paginate(
            HostedZoneId=hosted_zone["Id"], StartRecordName="_", StartRecordType="NS"
        )
        i = 0
        for page_records in pages_records:
            record_sets = [
                r for r in page_records["ResourceRecordSets"] if r["Type"] == "NS" and r["Name"] != hosted_zone["Name"]
            ]
            for record in record_sets:
                i = i + 1
                result = vulnerable_ns(record["Name"])

                if result:
                    vulnerable_domains.append(record["Name"])
                    my_print(f"{str(i)}. {record['Name']}", "ERROR")
                else:
                    my_print(f"{str(i)}. {record['Name']}", "SECURE")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Prevent Subdomain Takeover")
    parser.add_argument("--profile", required=True)
    args = parser.parse_args()
    profile = args.profile

    route53(profile)

    count = len(vulnerable_domains)
    my_print("\nTotal Vulnerable Domains Found: " + str(count), "INFOB")

    if count > 0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains)
