#!/usr/bin/env python
import json

from utils.utils_aws import publish_to_sns

from utils.utils_cloudflare import list_cloudflare_zones, list_cloudflare_records
from utils.utils_dns import vulnerable_ns, vulnerable_cname
from utils.utils_db import db_vulnerability_found, db_get_unfixed_vulnerability_found_date_time
from utils.utils_requests import vulnerable_storage, get_bucket_name


def process_vulnerability(domain, account_name, resource_type, vulnerability_type, takeover=""):

    # check if vulnerability has already been identified
    if db_get_unfixed_vulnerability_found_date_time(domain):
        print(f"{domain} in {account_name} is still vulnerable")

    # if it's a new vulnerability, add to JSON and write to DynamoDB
    else:
        print(f"New vulnerability {domain} in {account_name}")
        vulnerable_domains.append(domain)

        if account_name == "Cloudflare":
            cloud = "Cloudflare"
        else:
            cloud = "AWS"

        if takeover:
            json_data["New"].append(
                {
                    "Account": account_name,
                    "Cloud": cloud,
                    "Domain": domain,
                    "ResourceType": resource_type,
                    "VulnerabilityType": vulnerability_type,
                    "Takeover": takeover,
                }
            )

        else:
            json_data["New"].append(
                {
                    "Account": account_name,
                    "Cloud": cloud,
                    "Domain": domain,
                    "ResourceType": resource_type,
                    "VulnerabilityType": vulnerability_type,
                }
            )

        db_vulnerability_found(domain, account_name, vulnerability_type, resource_type)


def get_s3_region(domain):
    # get region from S3 FQDN, for any of the 3 different formats

    if ".s3-website-" in domain:
        bucket_region = domain.rsplit(".", 3)[1].split("-", 2)[2]

        return bucket_region

    bucket_region = domain.rsplit(".", 4)[2]

    return bucket_region


def cf_ns_subdomain(account_name, zone_name, records):

    records_filtered = [r for r in records if r["Type"] == "NS" and r["Name"] != zone_name]

    for record in records_filtered:
        domain = record["Name"]
        print(f"testing {domain} in {account_name} DNS zone {zone_name}")
        result = vulnerable_ns(domain)
        if result:
            process_vulnerability(domain, account_name, "hosted zone", "NS")


def cf_cname(account_name, zone_name, records):

    vulnerability_list = [
        "azure",
        ".cloudapp.net",
        "core.windows.net",
        "trafficmanager.net",
        "c.storage.googleapis.com",
    ]

    records_filtered = [
        r
        for r in records
        if r["Type"] in ["CNAME"] and any(vulnerability in r["Value"] for vulnerability in vulnerability_list)
    ]

    for record in records_filtered:
        domain = record["Name"]
        print(f"testing {domain} in {account_name} DNS zone {zone_name}")
        result = vulnerable_cname(domain)
        if result:
            process_vulnerability(domain, "Cloudflare", "cloud resources", "CNAME")


def cf_s3(account_name, zone_name, records):

    vulnerability_list = [".s3"]

    records_filtered = [
        r
        for r in records
        if r["Type"] in ["CNAME"] and any(vulnerability in r["Value"] for vulnerability in vulnerability_list)
    ]

    for record in records_filtered:

        domain = record["Name"]
        value = record["Value"]

        print(f"testing {domain} in {account_name} DNS zone {zone_name}")

        if ".s3" in value and vulnerable_storage(domain):
            print(f"VULNERABLE CNAME {domain} pointing to missing S3 bucket {value}")

            # get the bucket name from the web response in case CloudFlare proxy is in free plan account
            bucket_name = get_bucket_name(domain)

            # get bucket region from FQDN to include in takeover target
            region = get_s3_region(value)

            # construct target FQDN to pass to takeover.py via SNS topic
            takeover = f"{bucket_name}.s3-website.{region}.amazonaws.com"

            # check if vulnerability is already in DynamoDB and raise alert if needed
            process_vulnerability(domain, "Cloudflare", "S3", "CNAME", takeover)


def cf_eb(account_name, zone_name, records):

    vulnerability_list = [".elasticbeanstalk.com"]

    records_filtered = [
        r
        for r in records
        if r["Type"] in ["CNAME"] and any(vulnerability in r["Value"] for vulnerability in vulnerability_list)
    ]

    for record in records_filtered:

        domain = record["Name"]
        value = record["Value"]

        print(f"testing {domain} in {account_name} DNS zone {zone_name}")

        result = vulnerable_cname(domain)

        if result:
            print(f"VULNERABLE CNAME {domain} pointing to missing Elastic Beanstalk environment {value}")

            # check if vulnerability is already in DynamoDB and raise alert if needed
            process_vulnerability(domain, "Cloudflare", "Elastic Beanstalk", "CNAME", value)


def lambda_handler(event, context):  # pylint:disable=unused-argument

    global vulnerable_domains
    vulnerable_domains = []

    global json_data
    json_data = {"New": []}

    zones = list_cloudflare_zones()

    for zone in zones:
        print(f"Searching for vulnerable subdomain records in Cloudflare DNS zone {zone['Name']}")

        zone_id = zone["Id"]
        zone_name = zone["Name"]

        records = list_cloudflare_records(zone_id, zone_name)

        cf_ns_subdomain("Cloudflare", zone_name, records)
        cf_cname("Cloudflare", zone_name, records)
        cf_s3("Cloudflare", zone_name, records)
        cf_eb("Cloudflare", zone_name, records)

    print(json.dumps(json_data, sort_keys=True, indent=2))

    if len(vulnerable_domains) > 0:
        publish_to_sns(json_data, "New domains vulnerable to takeover")
