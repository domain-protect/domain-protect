#!/usr/bin/env python
import argparse

import boto3
import dns.resolver
import requests

from utils.utils_aws_manual import list_hosted_zones_manual_scan
from utils.utils_dns import firewall_test
from utils.utils_print import my_print
from utils.utils_print import print_list

vulnerable_domains = []


def vulnerable_cname_s3(domain_name):

    try:
        response = requests.get("http://" + domain_name, timeout=1)

        if response.status_code == 404 and "Code: NoSuchBucket" in response.text:
            return True

    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        pass

    return False


def route53(profile):

    print("Searching for Route53 hosted zones")

    session = boto3.Session(profile_name=profile)
    route53 = session.client("route53")

    hosted_zones = list_hosted_zones_manual_scan(profile)
    for hosted_zone in hosted_zones:
        print(f"Searching for S3 CNAME records in hosted zone {hosted_zone['Name']}")
        paginator_records = route53.get_paginator("list_resource_record_sets")
        pages_records = paginator_records.paginate(
            HostedZoneId=hosted_zone["Id"],
            StartRecordName="_",
            StartRecordType="CNAME",
        )
        i = 0
        for page_records in pages_records:
            record_sets = [
                r
                for r in page_records["ResourceRecordSets"]
                if r["Type"] in ["CNAME"]
                and r.get("ResourceRecords")
                and "amazonaws.com" in r["ResourceRecords"][0]["Value"]
                and ".s3-website." in r["ResourceRecords"][0]["Value"]
            ]
            for record in record_sets:
                print(f"checking if {record['Name']} is vulnerable to takeover")
                i = i + 1
                result = vulnerable_cname_s3(record["Name"])
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

    firewall_test()
    route53(profile)

    count = len(vulnerable_domains)
    my_print("\nTotal Vulnerable Domains Found: " + str(count), "INFOB")

    if count > 0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains)

        print("")
        my_print("Create S3 buckets with these domain names to prevent takeover:", "INFOB")
        i = 0
        for vulnerable_domain in vulnerable_domains:
            result = dns.resolver.resolve(vulnerable_domain, "CNAME")
            for cname_value in result:
                i = i + 1
                cname = cname_value.target
                cname_string = str(cname)
                my_print(str(i) + ". " + cname_string, "OUTPUT_WS")
