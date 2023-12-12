import warnings

import boto3
import regex
import requests
import urllib3


def list_hosted_zones_manual_scan():
    session = boto3.Session()
    route53 = session.client("route53")

    hosted_zones_list = []

    paginator_zones = route53.get_paginator("list_hosted_zones")
    pages_zones = paginator_zones.paginate()
    for page_zones in pages_zones:
        hosted_zones = [h for h in page_zones["HostedZones"] if not h["Config"]["PrivateZone"]]

        hosted_zones_list = hosted_zones_list + hosted_zones

    return hosted_zones_list


# Given the bucket's direct URL or S3 website URL, returns True if the bucket does not exist
def bucket_does_not_exist(bucket_url):
    try:
        # NOTE: We don't verify TLS, because the certificate matches the CloudFront's distribution domain name, not the S3 bucket's domain name
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)
            response = requests.get("https://" + bucket_url, timeout=1, verify=False)  # nosec B501

        # When accessed directly e.g. bucket.s3.amazonaws.com
        if response.status_code == 404 and "<Code>NoSuchBucket</Code>" in response.text:
            return True

        # When accessed through S3 website url e.g. bucket.s3-website-us-east-1.amazonaws.com
        if response.status_code == 404 and "Code: NoSuchBucket" in response.text:
            return True

    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        pass

    return False


# Extracts the origin URL from a CloudFront distribution
def get_cloudfront_origin_url(domain_name):
    boto3_session = boto3.Session()
    cloudfront = boto3_session.client("cloudfront")

    # List CloudFront distributions, find the one with the matching domain name
    paginator = cloudfront.get_paginator("list_distributions")
    pages = paginator.paginate()
    for page in pages:
        for distribution in page["DistributionList"]["Items"]:
            for alias in distribution["Aliases"]["Items"]:
                if alias + "." == domain_name:
                    # We found the right distribution
                    return distribution["Origins"]["Items"][0]["DomainName"]


def is_s3_bucket_url(url):
    # bucket.s3.amazonaws.com or bucket.s3.region.amazonaws.com
    return url is not None and regex.match(r"^.+\.s3.([a-z0-9-]+\.)?amazonaws.com$", url) is not None


def is_s3_website_endpoint_url(url):
    # bucket.s3-website-region.amazonaws.com
    return url is not None and regex.match(r"^.+\.s3-website[-\.]([a-z0-9-]+\.)?amazonaws.com$", url) is not None
