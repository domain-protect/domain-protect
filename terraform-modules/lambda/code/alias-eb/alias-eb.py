#!/usr/bin/env python
import json
import dns.resolver

from utils_aws import (
    list_accounts,
    list_hosted_zones,
    list_resource_record_set_pages,
    publish_to_sns,
)


def vulnerable_alias_eb(domain_name):

    try:
        dns.resolver.resolve(domain_name, "A")
        return False

    except dns.resolver.NoAnswer:
        return True

    except (dns.resolver.NoNameservers, dns.resolver.NXDOMAIN):
        return False


def lambda_handler(event, context):  # pylint:disable=unused-argument

    vulnerable_domains = []
    json_data = {"Findings": []}

    accounts = list_accounts()

    for account in accounts:
        account_id = account["Id"]
        account_name = account["Name"]

        hosted_zones = list_hosted_zones(account)
        for hosted_zone in hosted_zones:

            print(f"Searching for Elastic Beanstalk alias records in hosted zone {hosted_zone['Name']}")

            pages_records = list_resource_record_set_pages(account_id, account_name, hosted_zone["Id"])

            for page_records in pages_records:
                record_sets = [
                    r
                    for r in page_records["ResourceRecordSets"]
                    if "AliasTarget" in r and "elasticbeanstalk.com" in r["AliasTarget"]["DNSName"]
                ]

                for record in record_sets:
                    print(f"checking if {record['Name']} is vulnerable to takeover")
                    result = vulnerable_alias_eb(record["Name"])
                    if result:
                        print(f"{record['Name']} in {account_name} is vulnerable")
                        vulnerable_domains.append(record["Name"])
                        json_data["Findings"].append(
                            {"Account": account_name, "AccountID": str(account_id), "Domain": record["Name"]}
                        )

    if len(hosted_zones) == 0:
        print(f"No hosted zones found in {account_name} account")

    print(json.dumps(json_data, sort_keys=True, indent=2))

    if len(vulnerable_domains) > 0:
        publish_to_sns(json_data, "Vulnerable Elastic Beanstalk alias records found in Amazon Route53")
