#!/usr/bin/env python

from utils.utils_print import my_print, print_list
from utils.utils_dns import vulnerable_ns
from utils.utils_cloudflare import list_cloudflare_records, list_cloudflare_zones


vulnerable_domains = []


def main():
    print("Searching for vulnerable NS subdomains ...")
    i = 0
    zones = list_cloudflare_zones()

    for zone in zones:
        records = list_cloudflare_records(zone["Id"], zone["Name"])

        ns_records = [r for r in records if r["Type"] == "NS" and r["Name"] != zone["Name"]]
        for record in ns_records:
            i = i + 1
            result = vulnerable_ns(record["Name"])

            if result and record["Name"] not in vulnerable_domains:
                vulnerable_domains.append(record["Name"])
                my_print(f"{str(i)}. {record['Name']}", "ERROR")

            if not result:
                my_print(f"{str(i)}. {record['Name']}", "SECURE")

    count = len(vulnerable_domains)
    my_print("\nTotal vulnerable NS subdomains found: " + str(count), "INFOB")

    if count > 0:
        my_print("Vulnerable NS subdomains:", "INFOB")
        print_list(vulnerable_domains)


if __name__ == "__main__":
    main()
