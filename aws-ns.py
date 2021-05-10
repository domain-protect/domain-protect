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

vulnerableDomains=[]
suspectedDomains=[]
isException=False
x=0
nsRecords=0
aRecords=0
verboseMode=False

def my_print(text, type):
    if type=="INFO":
        if verboseMode:
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

    global nsRecords, aRecords, isException
    isException=False
    nsRecords=0
    try:
        aRecords= dns.resolver.resolve(domain_name)
    except dns.resolver.NXDOMAIN:
        return False, "\tI: "+domain_name+"  Not Registered-> Getting NXDOMAIN Exception"
    except dns.resolver.NoNameservers:
        try:
            nsRecords = dns.resolver.resolve(domain_name, 'NS')
        except:
            isException=True
            return False, "\tI: Exception While Fetching NS Records of "+domain_name
        if len(nsRecords)==0:
            return False
        return True, ""
    except:
        pass
    return False, ""

class route53:
    def __init__(self, profile):
        self.profile = profile

        print("Searching for Route53 hosted zones")
        self.session = boto3.session.Session(profile_name=self.profile)
        self.client = self.session.client('route53')
        hosted_zones = self.client.list_hosted_zones()['HostedZones']
        #print(json.dumps(hosted_zones, sort_keys=True, indent=2, default=json_serial))
        for hosted_zone in hosted_zones:
            if not hosted_zone['Config']['PrivateZone']:
                print("Searching for subdomain NS records in hosted zone %s" % (hosted_zone['Name']) )
                record_sets = self.client.list_resource_record_sets(HostedZoneId=hosted_zone['Id'])
                #print(json.dumps(record_sets, sort_keys=True, indent=2, default=json_serial))
                i=0
                for record in record_sets['ResourceRecordSets']:
                    if record['Type'] in ['NS']:
                        if record['Name'] != hosted_zone['Name']:
                            i=i+1
                            ns_record = record['Name']
                            result, exception_message=vulnerable_ns(ns_record)
                            if result:
                                vulnerableDomains.append(ns_record)
                                my_print(str(i)+". "+ns_record,"ERROR")
                            elif (result==False) and (isException==True):
                                suspectedDomains.append(ns_record)
                                my_print(str(i)+". "+ns_record,"INFOB")
                                my_print(exception_message, "INFO")
                            else:
                                my_print(str(i)+". "+ns_record,"SECURE")
                                my_print(exception_message, "INFO")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Prevent Subdomain Takeover")
    parser.add_argument('--profile', required=True)
    args = parser.parse_args()
    profile = args.profile

    route53(profile)

    countV=len(vulnerableDomains)
    my_print("\nTotal Vulnerable Domains Found: "+str(countV), "INFOB")
    countS=len(suspectedDomains)
    my_print("Total Suspected Domains Found: "+str(countS)+"\n", "INFOB")
    if countV>0:
        my_print("List of Vulnerable Domains:", "INFOB")
        print_list(vulnerableDomains)
    if countS>0:
        my_print("List of Suspected Domains:", "INFOB")
        print_list(suspectedDomains)