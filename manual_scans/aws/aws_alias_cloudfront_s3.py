#!/usr/bin/env python
import boto3

from utils.utils_aws_manual import list_hosted_zones_manual_scan
from utils.utils_aws_manual import vulnerable_alias_cloudfront_s3
from utils.utils_print import my_print
from utils.utils_print import print_list


def route53():
    vulnerable_domains = []
    missing_resources = []

    print("Searching for Route53 hosted zones")

    session = boto3.Session()
    route53 = session.client("route53")

    hosted_zones = list_hosted_zones_manual_scan()
    for hosted_zone in hosted_zones:
        print(f"Searching for CloudFront Alias records in {hosted_zone['Name']}")
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
                if "AliasTarget" in r and "cloudfront.net" in r["AliasTarget"]["DNSName"] and "AAAA" not in r["Type"]
            ]
            for record in record_sets:
                i = i + 1
                result = vulnerable_alias_cloudfront_s3(record["Name"])
                if result:
                    vulnerable_domains.append(record["Name"])
                    my_print(f"{str(i)}. {record['Name']}", "ERROR")
                    missing_resources.append(record["AliasTarget"]["DNSName"])
                else:
                    my_print(f"{str(i)}. {record['Name']}", "SECURE")

    return vulnerable_domains, missing_resources


def main():
    vulnerable_domains, missing_resources = route53()

    count = len(vulnerable_domains)
    my_print(f"\nTotal Vulnerable Domains Found: {str(count)}", "INFOB")

    if count > 0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains, "INSECURE_WS")

        my_print("\nCloudFront distributions with missing S3 origin: ", "INFOB")
        print_list(missing_resources, "OUTPUT_WS")


if __name__ == "__main__":
    main()
