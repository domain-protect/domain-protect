#!/usr/bin/env python
import argparse

import boto3

from utils.utils_dns import firewall_test
from utils.utils_dns import vulnerable_ns
from utils.utils_print import my_print
from utils.utils_print import print_list

vulnerable_domains = []


def route53domains():

    print("Searching for Route53 registered domains")

    session = boto3.Session(region_name="us-east-1")
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
    
    firewall_test()
    route53domains()

    count = len(vulnerable_domains)
    my_print("\nTotal Vulnerable Domains Found: " + str(count), "INFOB")

    if count > 0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains)
