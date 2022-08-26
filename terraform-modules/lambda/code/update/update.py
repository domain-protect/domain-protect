#!/usr/bin/env python
import json
import os

from utils.utils_aws import publish_to_sns, domain_deleted
from utils.utils_aws_ips import vulnerable_aws_a_record
from utils.utils_db import db_list_all_unfixed_vulnerabilities, db_vulnerability_fixed
from utils.utils_dns import dns_deleted, vulnerable_ns, vulnerable_alias, vulnerable_cname
from utils.utils_requests import vulnerable_storage, get_all_aws_ips
from utils.utils_sanitise import restore_wildcard, sanitise_domain

ip_time_limit = os.environ["IP_TIME_LIMIT"]


def lambda_handler(event, context):  # pylint:disable=unused-argument

    vulnerabilities = db_list_all_unfixed_vulnerabilities()
    json_data = {"Fixed": []}
    prefixes = get_all_aws_ips()
    ip_prefixes = [i["ip_prefix"] for i in prefixes]

    for vulnerability in vulnerabilities:
        domain = vulnerability["Domain"]["S"]
        domain = sanitise_domain(domain)
        vulnerability_type = vulnerability["VulnerabilityType"]["S"]
        resource_type = vulnerability["ResourceType"]["S"]
        cloud = vulnerability["Cloud"]["S"]
        account = vulnerability["Account"]["S"]

        if vulnerability_type == "NS":
            if dns_deleted(domain, "NS") or not vulnerable_ns(domain, True):
                domain = restore_wildcard(domain)
                db_vulnerability_fixed(domain)
                json_data["Fixed"].append(
                    {"Account": account, "Cloud": cloud, "Domain": domain, "ResourceType": resource_type}
                )

        elif "S3" in resource_type or "Google cloud storage" in resource_type:
            if dns_deleted(domain, "CNAME") or not vulnerable_storage(domain, https_timeout=3, http_timeout=3):
                domain = restore_wildcard(domain)
                db_vulnerability_fixed(domain)
                json_data["Fixed"].append(
                    {"Account": account, "Cloud": cloud, "Domain": domain, "ResourceType": resource_type}
                )

        elif vulnerability_type == "CNAME":
            if dns_deleted(domain, "CNAME") or not vulnerable_cname(domain, True):
                domain = restore_wildcard(domain)
                db_vulnerability_fixed(domain)
                json_data["Fixed"].append(
                    {"Account": account, "Cloud": cloud, "Domain": domain, "ResourceType": resource_type}
                )

        elif vulnerability_type == "Alias":
            if dns_deleted(domain) or not vulnerable_alias(domain, True):
                domain = restore_wildcard(domain)
                db_vulnerability_fixed(domain)
                json_data["Fixed"].append(
                    {"Account": account, "Cloud": cloud, "Domain": domain, "ResourceType": resource_type}
                )

        elif vulnerability_type == "A":
            if dns_deleted(domain) or not vulnerable_aws_a_record(ip_prefixes, resource_type, ip_time_limit):
                domain = restore_wildcard(domain)
                db_vulnerability_fixed(domain)
                json_data["Fixed"].append(
                    {"Account": account, "Cloud": cloud, "Domain": domain, "ResourceType": resource_type}
                )

        elif vulnerability_type == "registered domain":
            if domain_deleted(domain, account) or not vulnerable_ns(domain, True):
                domain = restore_wildcard(domain)
                db_vulnerability_fixed(domain)
                json_data["Fixed"].append(
                    {"Account": account, "Cloud": cloud, "Domain": domain, "ResourceType": resource_type}
                )

    if len(json_data["Fixed"]) == 0:
        print("No new fixed vulnerabilities")

    else:
        print(json.dumps(json_data, sort_keys=True, indent=2))
        publish_to_sns(json_data, "Domains no longer vulnerable to takeover")
