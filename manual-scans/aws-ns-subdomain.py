#!/usr/bin/env python
import argparse

import boto3
import dns.resolver

from utils import my_print, print_list

vulnerable_domains = []


def vulnerable_ns(domain_name):

    try:
        dns.resolver.resolve(domain_name)

    except dns.resolver.NXDOMAIN:
        return False

    except dns.resolver.NoNameservers:

        try:
            ns_records = dns.resolver.resolve(domain_name, "NS")
            if len(ns_records) == 0:
                return True

        except dns.resolver.NoNameservers:
            return True

    except dns.resolver.NoAnswer:
        return False

    return False


def route53(profile):

    print("Searching for Route53 hosted zones")

    session = boto3.Session(profile_name=profile)
    route53 = session.client("route53")

    paginator_zones = route53.get_paginator("list_hosted_zones")
    pages_zones = paginator_zones.paginate()
    for page_zones in pages_zones:
        hosted_zones = [h for h in page_zones["HostedZones"] if not h["Config"]["PrivateZone"]]
        for hosted_zone in hosted_zones:
            print("Searching for subdomain NS records in hosted zone %s" % (hosted_zone["Name"]))
            paginator_records = route53.get_paginator("list_resource_record_sets")
            pages_records = paginator_records.paginate(
                HostedZoneId=hosted_zone["Id"], StartRecordName="_", StartRecordType="NS"
            )
            i = 0
            for page_records in pages_records:
                # record_sets = page_records['ResourceRecordSets']
                record_sets = [
                    r
                    for r in page_records["ResourceRecordSets"]
                    if r["Type"] == "NS" and r["Name"] != hosted_zone["Name"]
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
