#!/usr/bin/env python
import argparse
import boto3
from utils.utils_aws import eb_susceptible
from utils.utils_aws_manual import list_hosted_zones_manual_scan
from utils.utils_dns import firewall_test
from utils.utils_dns import vulnerable_alias
from utils.utils_print import my_print
from utils.utils_print import print_list

vulnerable_domains = []
missing_resources = []


def route53():

    print("Searching for Route53 hosted zones")

    session = boto3.Session()
    route53 = session.client("route53")

    hosted_zones = list_hosted_zones_manual_scan()
    for hosted_zone in hosted_zones:
        print(f"Searching for ElasticBeanststalk Alias records in hosted zone {hosted_zone['Name']}")
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
                if "AliasTarget" in r and eb_susceptible(r["AliasTarget"]["DNSName"])
            ]

            for record in record_sets:
                print(f"checking if {record['Name']} is vulnerable to takeover")
                i = i + 1
                result = vulnerable_alias(record["Name"])
                if result:
                    vulnerable_domains.append(record["Name"])
                    my_print(f"{str(i)}. {record['Name']}", "ERROR")
                    missing_resources.append(record["AliasTarget"]["DNSName"])
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
        print_list(vulnerable_domains, "INSECURE_WS")

        my_print("\nCreate these resources to prevent takeover: ", "INFOB")
        print_list(missing_resources, "OUTPUT_WS")
