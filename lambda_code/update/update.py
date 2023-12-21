#!/usr/bin/env python
import json
import os

from utils.utils_aws import domain_deleted
from utils.utils_aws import publish_to_sns
from utils.utils_aws_ips import vulnerable_aws_a_record
from utils.utils_db import db_list_all_unfixed_vulnerabilities
from utils.utils_db import db_vulnerability_fixed
from utils.utils_dns import dns_deleted
from utils.utils_dns import updated_a_record
from utils.utils_dns import vulnerable_alias
from utils.utils_dns import vulnerable_cname
from utils.utils_dns import vulnerable_ns
from utils.utils_requests import cloudfront_s3_fixed
from utils.utils_requests import get_all_aws_ips
from utils.utils_requests import vulnerable_storage
from utils.utils_sanitise import restore_wildcard
from utils.utils_sanitise import sanitise_domain

ip_time_limit = os.environ["IP_TIME_LIMIT"]


def vulnerability_fixed_actions(json_data, account, cloud, domain, resource_type):

    domain = restore_wildcard(domain)
    db_vulnerability_fixed(domain)
    json_data["Fixed"].append({"Account": account, "Cloud": cloud, "Domain": domain, "ResourceType": resource_type})

    return json_data


def get_fixed_predicates():
    # Conditions to check. All lambdas need to have same parameter list
    # Parameters can be ignored in lambda body

    return [
        lambda v, d, r, i: v == "NS" and (dns_deleted(d, "NS") or not vulnerable_ns(d, True)),
        lambda v, d, r, i: v == "CNAME"
        and (r == "S3" or "Google cloud storage" in r)
        and (dns_deleted(d, "CNAME") or not vulnerable_storage(d, https_timeout=3, http_timeout=3)),
        lambda v, d, r, i: (r == "S3" or "Google cloud storage" in r)
        and (dns_deleted(d) or not vulnerable_storage(d, https_timeout=3, http_timeout=3)),
        lambda v, d, r, i: v == "CNAME" and r == "CloudFront S3" and (dns_deleted(d) or cloudfront_s3_fixed(d)),
        lambda v, d, r, i: v == "CNAME"
        and r != "CloudFront S3"
        and (dns_deleted(d, "CNAME") or not vulnerable_cname(d, True)),
        lambda v, d, r, i: v == "Alias" and r == "CloudFront S3" and (dns_deleted(d) or cloudfront_s3_fixed(d)),
        lambda v, d, r, i: v == "Alias" and r != "CloudFront S3" and (dns_deleted(d) or not vulnerable_alias(d, True)),
        lambda v, d, r, i: v == "A"
        and (dns_deleted(d) or not vulnerable_aws_a_record(i, updated_a_record(d, r), ip_time_limit)),
    ]


def is_fixed(predicates, vulnerability_type, domain, resource_type, ip_prefixes):
    for predicate in predicates:
        if predicate(vulnerability_type, domain, resource_type, ip_prefixes):
            return True

    return False


def lambda_handler(event, context):  # pylint:disable=unused-argument

    predicates = get_fixed_predicates()
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

        if is_fixed(predicates, vulnerability_type, domain, resource_type, ip_prefixes):
            json_data = vulnerability_fixed_actions(json_data, account, cloud, domain, resource_type)

        if vulnerability_type == "registered domain" and (
            domain_deleted(domain, account) or not vulnerable_ns(domain, True)
        ):
            json_data = vulnerability_fixed_actions(json_data, account, cloud, domain, resource_type)

    if len(json_data["Fixed"]) == 0:
        print("No new fixed vulnerabilities")

    else:
        print(json.dumps(json_data, sort_keys=True, indent=2))
        publish_to_sns(json_data, "Domains no longer vulnerable to takeover")
