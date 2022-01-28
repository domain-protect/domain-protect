import CloudFlare


def list_cloudflare_zones():

    cf = CloudFlare.CloudFlare(raw=True)
    print("Searching for DNS zones in Cloudflare")

    page_number = 0
    total_zones = 0
    zone_list = []

    while True:
        page_number += 1
        raw_results = cf.zones.get(params={"per_page": 5, "page": page_number})
        zones = raw_results["result"]

        for zone in zones:
            total_zones += 1
            zone_id = zone["id"]
            zone_name = zone["name"]
            zone_list.append({"Id": zone_id, "Name": zone_name})

        zone_total_pages = raw_results["result_info"]["total_pages"]
        if page_number == zone_total_pages:
            break

    print(f"returned {total_zones} Cloudflare DNS zones")

    return zone_list


def list_cloudflare_records(zone_id, zone_name):

    cf = CloudFlare.CloudFlare(raw=True)
    print(f"Searching for DNS records in Cloudflare DNS zone {zone_name}")

    page_number = 0
    total_records = 0
    record_list = []

    while True:
        page_number += 1
        raw_results = cf.zones.dns_records.get(zone_id, params={"per_page": 5, "page": page_number})
        records = raw_results["result"]

        for record in records:
            total_records += 1
            record_list.append(
                {"Name": record["name"], "Type": record["type"], "Value": record["content"], "Id": record["id"]}
            )

        zone_total_pages = raw_results["result_info"]["total_pages"]
        if page_number == zone_total_pages:
            break

    print(f"returned {total_records} Cloudflare DNS records")

    return record_list
