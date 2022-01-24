#!/usr/bin/env python

from utils_print import my_print, print_list
from utils_dns import vulnerable_cname
from utils_cloudflare import list_zones, list_dns_records


vulnerable_domains = []
vulnerability_list = ["azure", ".cloudapp.net", "core.windows.net", "elasticbeanstalk.com", "trafficmanager.net"]

if __name__ == "__main__":

    print("Searching for vulnerable CNAMEs ...")
    i = 0
    zones = list_zones()

    for zone in zones:
        records = list_dns_records(zone["Id"], zone["Name"])

        cname_records = [
            r
            for r in records
            if r["Type"] in ["CNAME"] and any(vulnerability in r["Value"] for vulnerability in vulnerability_list)
        ]
        for record in cname_records:
            i = i + 1
            result = vulnerable_cname(record["Name"])

            if result:
                vulnerable_domains.append(record["Name"])
                my_print(f"{str(i)}. {record['Name']}", "ERROR")
            else:
                my_print(f"{str(i)}. {record['Name']}", "SECURE")

    count = len(vulnerable_domains)
    my_print("\nTotal vulnerable CNAMEs found: " + str(count), "INFOB")

    if count > 0:
        my_print("Vulnerable CNAMEs:", "INFOB")
        print_list(vulnerable_domains)
