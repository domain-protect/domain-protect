#!/usr/bin/env python
import argparse
import boto3
from utils.utils_aws_manual import list_hosted_zones_manual_scan
from utils.utils_dns import firewall_test
from utils.utils_dns import vulnerable_ns
from utils.utils_print import my_print, print_list
from utils.utils_sanitise import filtered_ns_records

vulnerable_domains = []


def route53():
    session = boto3.Session()
    route53 = session.client("route53")

    print("Searching for Route53 hosted zones")
    hosted_zones = list_hosted_zones_manual_scan()
    for hosted_zone in hosted_zones:
        print(f"Searching for subdomain NS records in hosted zone {hosted_zone['Name']}")
        paginator_records = route53.get_paginator("list_resource_record_sets")
        pages_records = paginator_records.paginate(
            HostedZoneId=hosted_zone["Id"],
            StartRecordName="_",
            StartRecordType="NS",
        )
        i = 0
        for page_records in pages_records:
            record_sets = filtered_ns_records(page_records["ResourceRecordSets"], hosted_zone["Name"])
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

    firewall_test()
    route53()

    count = len(vulnerable_domains)
    my_print("\nTotal Vulnerable Domains Found: " + str(count), "INFOB")

    if count > 0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains)
