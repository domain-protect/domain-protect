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

class route53:
    def __init__(self, profile):
        self.profile = profile

        print("Searching for Route53 hosted zones")
        self.session = boto3.session.Session(profile_name=self.profile)
        self.client = self.session.client('route53')
        try:
            paginator_zones = self.client.get_paginator('list_hosted_zones')
            pages_zones = paginator_zones.paginate()
            for page_zones in pages_zones:
                hosted_zones = page_zones['HostedZones']
                #print(json.dumps(hosted_zones, sort_keys=True, indent=2, default=json_serial))
                for hosted_zone in hosted_zones:
                    if not hosted_zone['Config']['PrivateZone']:
                        print("Searching for subdomain NS records in hosted zone %s" % (hosted_zone['Name']) )
                        try:
                            paginator_records = self.client.get_paginator('list_resource_record_sets')
                            pages_records = paginator_records.paginate(HostedZoneId=hosted_zone['Id'], StartRecordName='_', StartRecordType='NS')
                            i=0
                            for page_records in pages_records:
                                record_sets = page_records['ResourceRecordSets']
                                #print(json.dumps(record_sets, sort_keys=True, indent=2, default=json_serial))
                                for record in record_sets:
                                    if record['Type'] in ['NS']:
                                        if record['Name'] != hosted_zone['Name']:
                                            i = i + 1
                                            ns_record = record['Name']
                                            result, exception_message = vulnerable_ns(ns_record)

                                            if result.startswith("True"):
                                                vulnerable_domains.append(ns_record)
                                                my_print(str(i) +". " + ns_record, "ERROR")
                                            else:
                                                my_print(str(i)+". "+ns_record,"SECURE")
                                                my_print(exception_message, "INFO")

                        except:
                            pass
        except:
            pass

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Prevent Subdomain Takeover")
    parser.add_argument('--profile', required=True)
    args = parser.parse_args()
    profile = args.profile

    route53(profile)

    count = len(vulnerable_domains)
    my_print("\nTotal Vulnerable Domains Found: "+str(count), "INFOB")

    if count > 0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains)
