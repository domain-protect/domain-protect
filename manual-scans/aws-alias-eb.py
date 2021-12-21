#!/usr/bin/env python
import boto3
import argparse

import dns.resolver

from utils import my_print, print_list


vulnerable_domains = []
missing_resources = []


def vulnerable_alias_eb(domain_name):

    try:
        dns.resolver.resolve(domain_name, "A")
        return False

    except dns.resolver.NoAnswer:
        return True

    except (dns.resolver.NoNameservers, dns.resolver.NXDOMAIN):
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
            print(f"Searching for ElasticBeanststalk Alias records in hosted zone {hosted_zone['Name']}")
            paginator_records = route53.get_paginator("list_resource_record_sets")
            pages_records = paginator_records.paginate(
                HostedZoneId=hosted_zone["Id"], StartRecordName="_", StartRecordType="NS"
            )
            i = 0
            for page_records in pages_records:
                record_sets = [
                    r
                    for r in page_records["ResourceRecordSets"]
                    if "AliasTarget" in r and "elasticbeanstalk.com" in r["AliasTarget"]["DNSName"]
                ]

                for record in record_sets:
                    print(f"checking if {record['Name']} is vulnerable to takeover")
                    i = i + 1
                    result = vulnerable_alias_eb(record["Name"])
                    if result:
                        vulnerable_domains.append(record["Name"])
                        my_print(f"{str(i)}. {record['Name']}", "ERROR")
                        missing_resources.append(record["AliasTarget"]["DNSName"])
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
        print_list(vulnerable_domains, "INSECURE_WS")

        my_print("\nCreate these resources to prevent takeover: ", "INFOB")
        print_list(missing_resources, "OUTPUT_WS")
