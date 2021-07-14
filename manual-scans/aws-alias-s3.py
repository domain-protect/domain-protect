#!/usr/bin/env python
import boto3
import json
import argparse

from botocore.exceptions import ClientError
from datetime import datetime
import requests

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
missing_resources=[]
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

def print_list(lst, type):
    counter=0
    for item in lst:
        counter=counter+1
        entry=str(counter)+". "+item
        my_print("\t"+entry, type)

def vulnerable_alias_s3(domain_name):

    try:
        response = requests.get('http://' + domain_name, timeout=1)

        if response.status_code == 404 and "Code: NoSuchBucket" in response.text:
            return True, ""

        else:
            return False, ""

    except:
        return False, ""

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
                        print("Searching for S3 Alias records in hosted zone %s" % (hosted_zone['Name']) )
                        try:
                            paginator_records = self.client.get_paginator('list_resource_record_sets')
                            pages_records = paginator_records.paginate(HostedZoneId=hosted_zone['Id'], StartRecordName='_', StartRecordType='NS')
                            i=0
                            for page_records in pages_records:
                                record_sets = page_records['ResourceRecordSets']
                                #print(json.dumps(record_sets, sort_keys=True, indent=2, default=json_serial))
                                for record in record_sets:
                                    if "AliasTarget" in record:
                                        if ("amazonaws.com" in record['AliasTarget']['DNSName']) and "s3-website" in (record['AliasTarget']['DNSName']):
                                            #print("checking if " + record['Name'] + " is vulnerable to takeover")
                                            i=i+1
                                            domain_name = record['Name']
                                            alias = record['AliasTarget']['DNSName']
                                            result, exception_message = vulnerable_alias_s3(domain_name)
                                            if result:
                                                vulnerable_domains.append(domain_name)
                                                my_print(str(i) + ". " + domain_name,"ERROR")
                                                missing_resources.append(domain_name + alias)
                                            else:
                                                my_print(str(i) + ". " + domain_name,"SECURE")
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

    countV=len(vulnerable_domains)
    my_print("\nTotal Vulnerable Domains Found: "+str(countV), "INFOB")

    if countV>0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains, "INSECURE_WS")

        my_print("\nCreate these resources to prevent takeover: ", "INFOB")
        print_list(missing_resources, "OUTPUT_WS")
