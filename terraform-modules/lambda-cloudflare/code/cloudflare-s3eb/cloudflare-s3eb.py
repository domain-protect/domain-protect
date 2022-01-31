#!/usr/bin/env python
import json

from utils.utils_aws import publish_to_sns
from utils.utils_dns import vulnerable_cname
from utils.utils_cloudflare import list_cloudflare_zones, list_cloudflare_records
from utils.utils_requests import vulnerable_storage, get_bucket_name


def get_s3_region(domain):
    # get region from S3 FQDN, for any of the 3 different formats

    if ".s3-website-" in domain:
        bucket_region = domain.rsplit(".", 3)[1].split("-", 2)[2]

        return bucket_region

    bucket_region = domain.rsplit(".", 4)[2]

    return bucket_region


def lambda_handler(event, context):  # pylint:disable=unused-argument

    vulnerable_domains = []
    vulnerability_list = [
        ".s3",
        ".elasticbeanstalk.com",
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

            if ".s3" in record["Value"] and vulnerable_storage(record["Name"]):
                print(f"VULNERABLE CNAME {record['Name']} pointing to missing S3 bucket {record['Value']}")

                # get the bucket name from the web response in case CloudFlare proxy is in free plan account
                bucket_name = get_bucket_name(record["Name"])

                # get bucket region from FQDN to include in takeover target
                region = get_s3_region(record["Value"])

                # construct target FQDN to pass to takeover.py via SNS topic
                takeover = f"{bucket_name}.s3-website.{region}.amazonaws.com"

                vulnerable_domains.append(record["Name"])
                json_data["Findings"].append(
                    {
                        "Account": "Cloudflare",
                        "AccountID": "Cloudflare",
                        "Domain": record["Name"],
                        "Takeover": takeover,
                    }
                )

            elif ".elasticbeanstalk.com" in record["Value"]:
                result = vulnerable_cname(record["Name"])

                if result:
                    print(
                        f"VULNERABLE CNAME {record['Name']} pointing to missing Elastic Beanstalk environment {record['Value']}"
                    )
                    vulnerable_domains.append(record["Name"])
                    json_data["Findings"].append(
                        {
                            "Account": "Cloudflare",
                            "AccountID": "Cloudflare",
                            "Domain": record["Name"],
                            "Takeover": record["Value"],
                        }
                    )

            else:
                print(f"{record['Name']} is OK")

    print(json.dumps(json_data, sort_keys=True, indent=2))

    if len(vulnerable_domains) > 0:
        publish_to_sns(json_data, "Vulnerable CNAME records found in Cloudflare")
