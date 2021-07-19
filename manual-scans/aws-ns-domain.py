#!/usr/bin/env python
import boto3
import json
import argparse

from botocore.exceptions import ClientError
from datetime import datetime
import dns.resolver

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")

class bcolors:
    TITLE = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    INFO = '\033[93m'
    OKRED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    BGRED = '\033[41m'
    UNDERLINE = '\033[4m'
    FGWHITE = '\033[37m'
    FAIL = '\033[95m'

vulnerable_domains=[]
verbose_mode=False

def my_print(text, type):
    if type=="INFO":
        if verbose_mode:
            print(bcolors.INFO+text+bcolors.ENDC)
        return
    if type=="PLAIN_OUTPUT_WS":
        print(bcolors.INFO+text+bcolors.ENDC)
        return
    if type=="INFOB":
        print(bcolors.INFO+bcolors.BOLD+text+bcolors.ENDC)
        return
    if type=="ERROR":
        print(bcolors.BGRED+bcolors.FGWHITE+bcolors.BOLD+text+bcolors.ENDC)
        return
    if type=="MESSAGE":
        print(bcolors.TITLE+bcolors.BOLD+text+bcolors.ENDC+"\n")
        return
    if type=="INSECURE_WS":
        print(bcolors.OKRED+bcolors.BOLD+text+bcolors.ENDC)
        return
    if type=="INSECURE":
        print(bcolors.OKRED+bcolors.BOLD+text+bcolors.ENDC+"\n")
        return
    if type=="OUTPUT":
        print(bcolors.OKBLUE+bcolors.BOLD+text+bcolors.ENDC+"\n")
        return
    if type=="OUTPUT_WS":
        print(bcolors.OKBLUE+bcolors.BOLD+text+bcolors.ENDC)
        return
    if type=="SECURE":
        print(bcolors.OKGREEN+bcolors.BOLD+text+bcolors.ENDC)

def print_list(lst):
    counter=0
    for item in lst:
        counter=counter+1
        entry=str(counter)+". "+item
        my_print("\t"+entry, "INSECURE_WS")

def vulnerable_ns(domain_name):

    try:
        dns.resolver.resolve(domain_name)
    except dns.resolver.NXDOMAIN:
        return "False", "\n "+ domain_name +" not registered - NXDOMAIN exception"
    except dns.resolver.NoNameservers:
        try:
            ns_records = dns.resolver.resolve(domain_name, 'NS')
            if len(ns_records) > 0:
                return "False", ""
            else:
                return "True", "\n No NS records listed for " + domain_name
        except:
            return "True", "\n No NS records found for " + domain_name
    except:
        return "False", ""

class route53domains:
    def __init__(self, profile):
        self.profile = profile

        print("Searching for Route53 registered domains")
        self.session = boto3.session.Session(profile_name=self.profile, region_name="us-east-1")
        self.client = self.session.client('route53domains')
        
        paginator_zones = self.client.get_paginator('list_domains')
        pages_zones = paginator_zones.paginate()
        i=0
        for page_zones in pages_zones:
            domains = page_zones['Domains']
            #print(json.dumps(domains, sort_keys=True, indent=2, default=json_serial))
            for domain in domains:
                i = i + 1
                domain_name = domain['DomainName']
                print("testing " + domain_name + " for vulnerability")
                result, exception_message = vulnerable_ns(domain_name)

                if result.startswith("True"):
                    vulnerable_domains.append(domain_name)
                    my_print(str(i) + ". " + domain_name, "ERROR")
                else:
                    my_print(str(i) + ". "+ domain_name,"SECURE")
                    my_print(exception_message, "INFO")
            if i == 0:
                print("No registered domains found in this account")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Prevent Subdomain Takeover")
    parser.add_argument('--profile', required=True)
    args = parser.parse_args()
    profile = args.profile

    route53domains(profile)

    count = len(vulnerable_domains)
    my_print("\nTotal Vulnerable Domains Found: "+str(count), "INFOB")

    if count > 0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains)
