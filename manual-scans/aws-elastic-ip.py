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

def elastic_ip_available(ip_address):
    ec2client = boto3.client('ec2')
    try:
        response = ec2client.allocate_address(Domain='vpc',Address=ip_address)
        print("Elastic IP address " + response['PublicIp'] + " obtained with Allocation ID " + response['AllocationId'])

        try:
            ec2client.release_address(AllocationId=response['AllocationId'])
            print("Elastic IP address " + response['PublicIp'] + " released")

        except:
            return "False"

        return "True"

    except:
        return "False"

class elastic_ip:
    def __init__(self, profile):
        self.profile = profile

        print("Searching for Route53 hosted zones")
        self.session = boto3.session.Session(profile_name=self.profile)
        self.client = self.session.client('route53')
        i = 0
        j = 0
        try:
            paginator_zones = self.client.get_paginator('list_hosted_zones')
            pages_zones = paginator_zones.paginate()
            for page_zones in pages_zones:
                hosted_zones = page_zones['HostedZones']
                #print(json.dumps(hosted_zones, sort_keys=True, indent=2, default=json_serial))
                for hosted_zone in hosted_zones:
                    if not hosted_zone['Config']['PrivateZone']:
                        print("Searching for A records in hosted zone %s" % (hosted_zone['Name']) )
                        try:
                            paginator_records = self.client.get_paginator('list_resource_record_sets')
                            pages_records = paginator_records.paginate(HostedZoneId=hosted_zone['Id'], StartRecordName='_', StartRecordType='NS')
                            for page_records in pages_records:
                                record_sets = page_records['ResourceRecordSets']
                                #print(json.dumps(record_sets, sort_keys=True, indent=2, default=json_serial))
                                for record in record_sets:
                                    #print(json.dumps(record, sort_keys=True, indent=2, default=json_serial))
                                    if record['Type'] in ['A'] and "AliasTarget" not in record:
                                        domain_name = record['Name']
                                        for a_record in record['ResourceRecords']:
                                            ip_address = a_record['Value']
                                            if not ip_address.startswith(("10.", "192.168.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.")):
                                                #print("checking if " + ip_address + " is an available Elastic IP")

                                                result = elastic_ip_available(ip_address)
                                                if result.startswith("True"):
                                                    i = i + 1
                                                    vulnerable_domains.append(domain_name)
                                                    my_print(str(i) +". " +(domain_name), "ERROR")
                                                else:
                                                    j = j + 1
                                                    my_print(str(j)+". "+(domain_name),"SECURE")

                        except:
                            pass
        except:
            pass

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Prevent Subdomain Takeover")
    parser.add_argument('--profile', required=True)
    args = parser.parse_args()
    profile = args.profile

    elastic_ip(profile)

    count = len(vulnerable_domains)
    my_print("\nTotal Vulnerable Domains Found: "+str(count), "INFOB")

    if count > 0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerable_domains)
