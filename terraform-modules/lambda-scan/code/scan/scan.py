#!/usr/bin/env python
import json

from utils.utils_aws import (
    list_hosted_zones,
    list_resource_record_sets,
    publish_to_sns,
)

from utils.utils_dns import vulnerable_ns
from utils.utils_db import db_vulnerability_found, db_get_unfixed_vulnerability_found_date_time


def lambda_handler(event, context):  # pylint:disable=unused-argument

    vulnerable_domains = []
    json_data = {"New": []}

    print(f"Input: {event}")

    account_id = event["Id"]
    account_name = event["Name"]

    hosted_zones = list_hosted_zones(event)

    for hosted_zone in hosted_zones:
        print(f"Searching for subdomain NS records in hosted zone {hosted_zone['Name']}")

        record_sets = list_resource_record_sets(account_id, account_name, hosted_zone["Id"])

        record_sets = [r for r in record_sets if r["Type"] == "NS" and r["Name"] != hosted_zone["Name"]]

        for record in record_sets:
            print(f"testing {record['Name']} in {account_name} account")

            # check if the domain is vulnerable
            result = vulnerable_ns(record["Name"])
            if result:
                # check if vulnerability has already been identified
                if db_get_unfixed_vulnerability_found_date_time(record["Name"]):
                    print(f"{record['Name']} in {account_name} is still vulnerable")

                # if it's a new vulnerability, add to JSON
                else:
                    print(f"New vulnerability {record['Name']} in {account_name}")
                    vulnerable_domains.append(record["Name"])
                    json_data["New"].append(
                        {
                            "Account": account_name,
                            "Cloud": "AWS",
                            "Domain": record["Name"],
                            "ResourceType": "hosted zone",
                            "VulnerabilityType": "NS",
                        }
                    )
                    db_vulnerability_found(record["Name"], account_name, "NS", "hosted zone")

    if len(hosted_zones) == 0:
        print(f"No hosted zones found in {account_name} account")

    print(json.dumps(json_data, sort_keys=True, indent=2))

    if len(vulnerable_domains) > 0:
        publish_to_sns(json_data, "New domains vulnerable to takeover")
