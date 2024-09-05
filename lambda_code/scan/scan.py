#!/usr/bin/env python
import json
import logging
import os

from utils.utils_aws import assume_role
from utils.utils_aws import eb_susceptible
from utils.utils_aws import get_cloudfront_s3_origin_takeover
from utils.utils_aws import list_domains
from utils.utils_aws import list_hosted_zones
from utils.utils_aws import list_resource_record_sets
from utils.utils_aws import publish_to_sns
from utils.utils_aws_requests import vulnerable_cloudfront_s3
from utils.utils_bugcrowd import bugcrowd_create_issue
from utils.utils_db import db_get_unfixed_vulnerability_found_date_time
from utils.utils_db import db_vulnerability_found
from utils.utils_dns import vulnerable_alias
from utils.utils_dns import vulnerable_cname
from utils.utils_dns import vulnerable_ns
from utils.utils_hackerone import hackerone_create_report
from utils.utils_requests import vulnerable_storage
from utils.utils_sanitise import filtered_ns_records
from utils.utils_sanitise import restore_wildcard
from utils.utils_sanitise import sanitise_wildcards

bugcrowd = os.environ["BUGCROWD"]
hackerone = os.environ["HACKERONE"]
env_name = os.environ["ENVIRONMENT"]
production_env = os.environ["PRODUCTION_ENVIRONMENT"]

BC_ACCT_ID_BLACKLIST = [
    "876504563909"
]

def process_vulnerability(domain, account_name, resource_type, vulnerability_type, takeover=""):

    # restore any wildcard domains
    domain = restore_wildcard(domain)

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
                },
            )

        elif bugcrowd == "enabled" and env_name == production_env:
            bugcrowd_issue_created = bugcrowd_create_issue(domain, resource_type, vulnerability_type)

            json_data["New"].append(
                {
                    "Account": account_name,
                    "Cloud": cloud,
                    "Domain": domain,
                    "ResourceType": resource_type,
                    "VulnerabilityType": vulnerability_type,
                    "Bugcrowd": bugcrowd_issue_created,
                    "HackerOne": "N/A",
                },
            )

        elif hackerone == "enabled" and env_name == production_env:
            hackerone_report_created = hackerone_create_report(domain, resource_type, vulnerability_type)

            json_data["New"].append(
                {
                    "Account": account_name,
                    "Cloud": cloud,
                    "Domain": domain,
                    "ResourceType": resource_type,
                    "VulnerabilityType": vulnerability_type,
                    "Bugcrowd": "N/A",
                    "HackerOne": hackerone_report_created,
                },
            )

        else:
            json_data["New"].append(
                {
                    "Account": account_name,
                    "Cloud": cloud,
                    "Domain": domain,
                    "ResourceType": resource_type,
                    "VulnerabilityType": vulnerability_type,
                },
            )

        db_vulnerability_found(domain, account_name, vulnerability_type, resource_type)


def alias_cloudfront_s3(account_name, record_sets, account_id):

    record_sets_filtered = [
        r
        for r in record_sets
        if "AliasTarget" in r and "cloudfront.net" in r["AliasTarget"]["DNSName"] and "AAAA" not in r["Type"]
    ]

    for record in record_sets_filtered:
        domain = record["Name"]
        print(f"checking if {domain} is vulnerable to takeover")
        result = vulnerable_cloudfront_s3(account_id, account_name, domain)
        if result:
            takeover = get_cloudfront_s3_origin_takeover(account_id, account_name, record["AliasTarget"]["DNSName"])
            process_vulnerability(domain, account_name, "CloudFront S3", "Alias", takeover)


def alias_eb(account_name, record_sets):

    record_sets_filtered = [
        r for r in record_sets if "AliasTarget" in r and eb_susceptible(r["AliasTarget"]["DNSName"])
    ]

    for record in record_sets_filtered:
        domain = record["Name"]
        print(f"checking if {domain} is vulnerable to takeover")
        result = vulnerable_alias(domain)
        if result:
            takeover = record["AliasTarget"]["DNSName"]
            process_vulnerability(domain, account_name, "Elastic Beanstalk", "Alias", takeover)


def alias_s3(account_name, record_sets):

    record_sets_filtered = [
        r
        for r in record_sets
        if "AliasTarget" in r
        if ("amazonaws.com" in r["AliasTarget"]["DNSName"]) and "s3-website" in (r["AliasTarget"]["DNSName"])
    ]

    for record in record_sets_filtered:
        domain = record["Name"]
        print(f"checking if {domain} is vulnerable to takeover")
        result = vulnerable_storage(domain, https=False)
        if result:
            takeover = domain + "s3-website." + record["AliasTarget"]["DNSName"].split("-", 2)[2]
            process_vulnerability(domain, account_name, "S3", "Alias", takeover)


def cname_azure(account_name, record_sets):

    vulnerability_list = ["azure", ".cloudapp.net", ".windows.net", "trafficmanager.net", "visualstudio.com"]

    record_sets_filtered = [
        r
        for r in record_sets
        if r["Type"] in ["CNAME"]
        and "ResourceRecords" in r
        and any(vulnerability in r["ResourceRecords"][0]["Value"] for vulnerability in vulnerability_list)
    ]

    for record in record_sets_filtered:
        domain = record["Name"]
        print(f"checking if {domain} is vulnerable to takeover")
        result = vulnerable_cname(domain)
        if result:
            process_vulnerability(domain, account_name, "Azure", "CNAME")


def cname_cloudfront_s3(account_name, record_sets, account_id):

    record_sets = [
        r
        for r in record_sets
        if r["Type"] == "CNAME" and r.get("ResourceRecords") and "cloudfront.net" in r["ResourceRecords"][0]["Value"]
    ]

    for record in record_sets:
        domain = record["Name"]
        print(f"checking if {domain} is vulnerable to takeover")
        result = vulnerable_cloudfront_s3(account_id, account_name, domain)
        if result:
            takeover = get_cloudfront_s3_origin_takeover(
                account_id,
                account_name,
                record["ResourceRecords"][0]["Value"],
            )
            process_vulnerability(domain, account_name, "CloudFront S3", "CNAME", takeover)


def cname_eb(account_name, record_sets):

    record_sets_filtered = [
        r
        for r in record_sets
        if r["Type"] in ["CNAME"] and "ResourceRecords" in r and eb_susceptible(r["ResourceRecords"][0]["Value"])
    ]

    for record in record_sets_filtered:
        domain = record["Name"]
        print(f"checking if {domain} is vulnerable to takeover")
        result = vulnerable_cname(domain)
        if result:
            takeover = record["ResourceRecords"][0]["Value"]
            process_vulnerability(domain, account_name, "Elastic Beanstalk", "CNAME", takeover)


def cname_google(account_name, record_sets):

    record_sets_filtered = [
        r
        for r in record_sets
        if r["Type"] in ["CNAME"]
        and "ResourceRecords" in r
        and "c.storage.googleapis.com" in r["ResourceRecords"][0]["Value"]
    ]

    for record in record_sets_filtered:
        domain = record["Name"]
        print(f"checking if {domain} is vulnerable to takeover")
        result = vulnerable_storage(domain, https=False)
        if result:
            takeover = record["ResourceRecords"][0]["Value"]
            process_vulnerability(domain, account_name, "Google cloud storage", "CNAME", takeover)


def cname_s3(account_name, record_sets):

    record_sets_filtered = [
        r
        for r in record_sets
        if r["Type"] in ["CNAME"]
        and "ResourceRecords" in r
        and "amazonaws.com" in r["ResourceRecords"][0]["Value"]
        and ".s3-website" in r["ResourceRecords"][0]["Value"]
    ]

    for record in record_sets_filtered:
        domain = record["Name"]
        print(f"checking if {domain} is vulnerable to takeover")
        result = vulnerable_storage(domain, https=False)
        if result:
            takeover = record["ResourceRecords"][0]["Value"]
            process_vulnerability(domain, account_name, "S3", "CNAME", takeover)


def ns_subdomain(account_name, hosted_zone, record_sets):

    record_sets_filtered = filtered_ns_records(record_sets, hosted_zone["Name"])

    for record in record_sets_filtered:
        domain = record["Name"]
        print(f"testing {domain} in {account_name} account")
        result = vulnerable_ns(domain)
        if result:
            process_vulnerability(domain, account_name, "hosted zone", "NS")


def domain_registrar(account_id, account_name):

    print(f"Searching for registered domains in {account_name} account")
    domains = list_domains(account_id, account_name)

    for domain in domains:
        print(f"testing {domain} in {account_name} account")
        result = vulnerable_ns(domain)
        if result:
            print(f"{domain} in {account_name} is vulnerable")
            process_vulnerability(domain, account_name, "hosted zone", "registered domain")

    if len(domains) == 0:
        print(f"No registered domains found in {account_name} account")


def lambda_handler(event, context):  # pylint:disable=unused-argument

    global vulnerable_domains
    vulnerable_domains = []

    global json_data
    json_data = {"New": []}

    print(f"Input: {event}")

    account_id = event["Id"]
    account_name = event["Name"]

    if account_id in BC_ACCT_ID_BLACKLIST:
        logging.info("account ID found on BC account blacklist, skipping...")

        return

    aws_session = assume_role(account_id)
    r53client = aws_session.client("route53")

    hosted_zones = list_hosted_zones(r53client, event)
    for hosted_zone in hosted_zones:
        print(f"Searching for vulnerable domain records in hosted zone {hosted_zone['Name']}")

        record_sets = list_resource_record_sets(r53client, account_name, hosted_zone["Id"])
        record_sets = sanitise_wildcards(record_sets)

        alias_cloudfront_s3(account_name, record_sets, account_id)
        alias_eb(account_name, record_sets)
        alias_s3(account_name, record_sets)
        # cname_azure(account_name, record_sets)
        cname_cloudfront_s3(account_name, record_sets, account_id)
        cname_eb(account_name, record_sets)
        # cname_google(account_name, record_sets)
        cname_s3(account_name, record_sets)
        ns_subdomain(account_name, hosted_zone, record_sets)

    if len(hosted_zones) == 0:
        print(f"No hosted zones found in {account_name} account")

    domain_registrar(account_id, account_name)

    print(json.dumps(json_data, sort_keys=True, indent=2))

    if len(vulnerable_domains) > 0:
        publish_to_sns(json_data, "New domains vulnerable to takeover")
