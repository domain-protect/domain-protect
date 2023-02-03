#!/usr/bin/env python
import argparse

import boto3
import dns.resolver

from utils.utils_aws_manual import list_hosted_zones_manual_scan
from utils.utils_dns import firewall_test
from utils.utils_dns import vulnerable_cname
from utils.utils_print import my_print
from utils.utils_print import print_list

vulnerable_domains = []


def route53(profile):

    print("Searching for Route53 hosted zones")

    session = boto3.Session(profile_name=profile)
    route53 = session.client("route53")

    hosted_zones = list_hosted_zones_manual_scan(profile)
    for hosted_zone in hosted_zones:
        print(f"Searching for ElasticBeanstalk CNAME records in hosted zone {hosted_zone['Name']}")
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
                if r["Type"] in ["CNAME"] and "elasticbeanstalk.com" in r["ResourceRecords"][0]["Value"]
            ]
            for record in record_sets:
                i = i + 1
                result = vulnerable_cname(record["Name"])
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
    my_print(f"\nTotal Vulnerable Domains Found: {str(count)}", "INFOB")
    if count > 0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains)

        print("")
        my_print("Create ElasticBeanstalk environments with these domain names to prevent takeover:", "INFOB")
        i = 0
        for vulnerable_domain in vulnerable_domains:
            result = dns.resolver.resolve(vulnerable_domain, "CNAME")
            for cname_value in result:
                i = i + 1
                cname = cname_value.target
                cname_string = str(cname)
                my_print(f"{str(i)}. {cname_string}", "OUTPUT_WS")
