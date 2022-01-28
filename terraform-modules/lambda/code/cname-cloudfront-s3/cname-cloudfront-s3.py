#!/usr/bin/env python
import json

from utils.aws import (
    list_accounts,
    list_hosted_zones,
    list_resource_record_sets,
    publish_to_sns,
    get_cloudfront_origin,
)

from utils.requests import vulnerable_storage


def lambda_handler(event, context):  # pylint:disable=unused-argument

    vulnerable_domains = []
    json_data = {"Findings": []}

    accounts = list_accounts()
    for account in accounts:
        account_id = account["Id"]
        account_name = account["Name"]

        hosted_zones = list_hosted_zones(account)

        for hosted_zone in hosted_zones:
            print(f"Searching for CloudFront CNAME records in hosted zone {hosted_zone['Name']}")

            record_sets = list_resource_record_sets(account_id, account_name, hosted_zone["Id"])

            record_sets = [
                r for r in record_sets if r["Type"] == "CNAME" and "cloudfront.net" in r["ResourceRecords"][0]["Value"]
            ]

            for record in record_sets:
                print(f"checking if {record['Name']} is vulnerable to takeover")
                result = vulnerable_storage(record["Name"])
                if result:
                    print(f"{record['Name']} in {account_name} is vulnerable")
                    vulnerable_domains.append(record["Name"])
                    json_data["Findings"].append(
                        {
                            "Account": account_name,
                            "AccountID": str(account_id),
                            "Domain": record["Name"],
                            "Takeover": get_cloudfront_origin(
                                account_id, account_name, record["ResourceRecords"][0]["Value"]
                            ),
                        }
                    )

    if len(hosted_zones) == 0:
        print(f"No hosted zones found in {account_name} account")

    print(json.dumps(json_data, sort_keys=True, indent=2))

    if len(vulnerable_domains) > 0:
        publish_to_sns(json_data, "Amazon Route53 CNAME record for CloudFront distribution with missing S3 origin")
