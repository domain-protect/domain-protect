import boto3


def list_hosted_zones(profile):
    session = boto3.Session(profile_name=profile)
    route53 = session.client("route53")

    hosted_zones_list = []

    paginator_zones = route53.get_paginator("list_hosted_zones")
    pages_zones = paginator_zones.paginate()
    for page_zones in pages_zones:
        hosted_zones = [h for h in page_zones["HostedZones"] if not h["Config"]["PrivateZone"]]

        hosted_zones_list = hosted_zones_list + hosted_zones

    return hosted_zones_list
