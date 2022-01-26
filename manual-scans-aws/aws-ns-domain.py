#!/usr/bin/env python
import boto3
import argparse

from utils_dns import vulnerable_ns
from utils_print import my_print, print_list

vulnerable_domains = []


def route53domains(profile):

    print("Searching for Route53 registered domains")

    session = boto3.Session(profile_name=profile, region_name="us-east-1")
    route53domains = session.client("route53domains")

    paginator_domains = route53domains.get_paginator("list_domains")
    pages_domains = paginator_domains.paginate()
    i = 0
    for page_domains in pages_domains:
        domains = page_domains["Domains"]
        for domain in domains:
            i = i + 1
            domain_name = domain["DomainName"]
            print(f"testing {domain_name} for vulnerability")
            result = vulnerable_ns(domain_name)

            if result:
                vulnerable_domains.append(domain_name)
                my_print(str(i) + ". " + domain_name, "ERROR")
            else:
                my_print(str(i) + ". " + domain_name, "SECURE")
        if i == 0:
            print("No registered domains found in this account")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Prevent Subdomain Takeover")
    parser.add_argument("--profile", required=True)
    args = parser.parse_args()
    profile = args.profile

    route53domains(profile)

    count = len(vulnerable_domains)
    my_print("\nTotal Vulnerable Domains Found: " + str(count), "INFOB")

    if count > 0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains)
