#!/usr/bin/env python
import json

from utils.utils_aws import publish_to_sns

from utils.utils_cloudflare import list_cloudflare_zones, list_cloudflare_records
from utils.utils_dns import vulnerable_cname
from utils.utils_requests import vulnerable_storage


def lambda_handler(event, context):  # pylint:disable=unused-argument

    vulnerable_domains = []
    vulnerability_list = [
        "azure",
        ".cloudapp.net",
        "core.windows.net",
        "trafficmanager.net",
        "c.storage.googleapis.com",
    ]
    json_data = {"Findings": []}

    zones = list_cloudflare_zones()

    for zone in zones:
        print(f"Searching for vulnerable CNAMEs in Cloudflare DNS zone {zone['Name']}")
        records = list_cloudflare_records(zone["Id"], zone["Name"])

        cname_records = [
            r
            for r in records
            if r["Type"] in ["CNAME"] and any(vulnerability in r["Value"] for vulnerability in vulnerability_list)
        ]
        for record in cname_records:
            print(f"testing {record['Name']}")
            result = vulnerable_cname(record["Name"])

            if result or ("c.storage.googleapis.com" in record["Value"] and vulnerable_storage(record["Name"])):
                print(f"{record['Name']} with CNAME {record['Value']} is vulnerable")
                vulnerable_domains.append(record["Name"])

                json_data["Findings"].append(
                    {"Account": "Cloudflare", "AccountID": "Cloudflare", "Domain": record["Name"]}
                )

            else:
                print(f"{record['Name']} is OK")

    print(json.dumps(json_data, sort_keys=True, indent=2))

    if len(vulnerable_domains) > 0:
        publish_to_sns(json_data, "Vulnerable CNAME records found in Cloudflare")
