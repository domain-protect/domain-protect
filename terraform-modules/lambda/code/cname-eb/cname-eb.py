#!/usr/bin/env python
import json
import dns.resolver

from utils_aws import (list_accounts,  # pylint:disable=import-error
                       list_hosted_zones, list_resource_record_set_pages,
                       publish_to_sns)


def vulnerable_cname(domain_name):

    try:
        dns.resolver.resolve(domain_name, "A")
        return False

    except dns.resolver.NXDOMAIN:
        try:
            dns.resolver.resolve(domain_name, "CNAME")
            return True

        except dns.resolver.NoNameservers:
            return False

    except (dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return False


def lambda_handler(event, context): # pylint:disable=unused-argument

    vulnerable_domains       = []
    json_data                = {"Findings": []}

    accounts = list_accounts()
    for account in accounts:
        account_id = account['Id']
        account_name = account['Name']
        
        hosted_zones = list_hosted_zones(account_id, account_name)
        for hosted_zone in hosted_zones:
            if not hosted_zone['Config']['PrivateZone']:
                print("Searching for Elastic Beanstalk CNAME records in hosted zone %s" % (hosted_zone['Name']))

                pages_records = list_resource_record_set_pages(account_id, account_name, hosted_zone["Id"])

                for page_records in pages_records:
                    record_sets = page_records['ResourceRecordSets']
                    for record in record_sets:
                        if record['Type'] in ['CNAME'] and "elasticbeanstalk.com" in record['ResourceRecords'][0]['Value']:
                            print("checking if " + record['Name'] + " is vulnerable to takeover")
                            domain_name = record['Name']
                            try:
                                result = vulnerable_cname(domain_name)
                                if result:
                                    print(domain_name + "in " + account_name + " is vulnerable")
                                    vulnerable_domains.append(domain_name)
                                    json_data["Findings"].append({"Account": account_name, "AccountID" : str(account_id), "Domain": domain_name})
                            except:
                                pass
            
    if len(hosted_zones) == 0:
        print("No hosted zones found in " + account_name + " account")

    print(json.dumps(json_data, sort_keys=True, indent=2))

    if len(vulnerable_domains) > 0:
        publish_to_sns(json_data, "Vulnerable Elastic Beanstalk CNAME records found in Amazon Route53")
