#!/usr/bin/env python
import argparse

import boto3
import dns.resolver
import requests

from utils.utils_aws_manual import bucket_does_not_exist
from utils.utils_aws_manual import get_cloudfront_origin_url
from utils.utils_aws_manual import is_s3_bucket_url
from utils.utils_aws_manual import list_hosted_zones_manual_scan
from utils.utils_dns import firewall_test
from utils.utils_print import my_print
from utils.utils_print import print_list


def vulnerable_cname_cloudfront_s3(domain_name):
    try:
        response = requests.get(f"https://{domain_name}", timeout=1)

        if response.status_code == 404 and "<Code>NotFound</Code>" in response.text:
            bucket_url = get_cloudfront_origin_url(domain_name)
            if not is_s3_bucket_url(bucket_url):
                return False

            return bucket_does_not_exist(bucket_url)

    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        pass

    return False


def route53():
    vulnerable_domains = []

    print("Searching for Route53 hosted zones")

    session = boto3.Session()
    route53 = session.client("route53")

    hosted_zones = list_hosted_zones_manual_scan()
    for hosted_zone in hosted_zones:
        print(f"Searching for CloudFront CNAME records in hosted zone {hosted_zone['Name']}")

        paginator_records = route53.get_paginator("list_resource_record_sets")
        pages_records = paginator_records.paginate(
            HostedZoneId=hosted_zone["Id"],
            StartRecordName="_",
            StartRecordType="CNAME",
        )
        i = 0
        for page_records in pages_records:
            record_sets = page_records["ResourceRecordSets"]

            record_sets = [
                r
                for r in page_records["ResourceRecordSets"]
                if r["Type"] == "CNAME"
                and r.get("ResourceRecords")
                and "cloudfront.net" in r["ResourceRecords"][0]["Value"]
            ]

            for record in record_sets:
                print(f"checking if {record['Name']} is vulnerable to takeover")
                i = i + 1
                result = vulnerable_cname_cloudfront_s3(record["Name"])
                if result:
                    vulnerable_domains.append(record["Name"])
                    my_print(f"{str(i)}. {record['Name']}", "ERROR")
                else:
                    my_print(f"{str(i)}. {record['Name']}", "SECURE")

    return vulnerable_domains


def main():
    parser = argparse.ArgumentParser(description="Prevent Subdomain Takeover")

    vulnerable_domains = route53()

    count = len(vulnerable_domains)
    my_print("\nTotal Vulnerable Domains Found: " + str(count), "INFOB")

    if count > 0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains, "INSECURE_WS")

        print("")
        my_print("CloudFront distributions with missing S3 origin:", "INFOB")
        i = 0
        for vulnerable_domain in vulnerable_domains:
            result = dns.resolver.Resolver().resolve(vulnerable_domain, "CNAME")
            for cname_value in result:
                i = i + 1
                cname = cname_value.target
                cname_string = str(cname)
                my_print(f"{str(i)}. {cname_string}", "OUTPUT_WS")


if __name__ == "__main__":
    firewall_test()  # don't run for integration tests
    main()