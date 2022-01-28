#!/usr/bin/env python
import json

from utils.utils_aws import publish_to_sns

from utils.utils_cloudflare import list_cloudflare_zones, list_cloudflare_records
from utils.utils_dns import vulnerable_ns


def lambda_handler(event, context):  # pylint:disable=unused-argument

    vulnerable_domains = []
    json_data = {"Cloudflare": []}

    zones = list_cloudflare_zones()

    for zone in zones:
        print(f"Searching for subdomain NS records in Cloudflare DNS zone {zone['Name']}")
        records = list_cloudflare_records(zone["Id"], zone["Name"])

        ns_records = [r for r in records if r["Type"] == "NS" and r["Name"] != zone["Name"]]
        for record in ns_records:
            print(f"testing {record['Name']}")
            result = vulnerable_ns(record["Name"])

            if result and record["Name"] not in vulnerable_domains:
                print(f"{record['Name']} is vulnerable")
                vulnerable_domains.append(record["Name"])
                json_data["Cloudflare"].append({"Domain": record["Name"]})

            if not result:
                print(f"{record['Name']} is OK")

    print(json.dumps(json_data, sort_keys=True, indent=2))

    if len(vulnerable_domains) > 0:
        publish_to_sns(json_data, "Vulnerable NS subdomain records found in Cloudflare")
