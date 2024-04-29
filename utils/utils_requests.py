import logging
import re

import requests

from utils.utils_globalvars import requests_timeout


def vulnerable_storage(domain_name, https=True, http=True, https_timeout=1, http_timeout=1):

    if https:
        try:
            response = requests.get("https://" + domain_name, timeout=https_timeout)
            if "NoSuchBucket" in response.text:
                return True

            if "Amazon CloudFront distribution is configured to block access from your country" in response.text:
                logging.error(
                    "Amazon CloudFront distribution for %s configured to block access from your country",
                    domain_name,
                )

        except (
            requests.exceptions.SSLError,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.TooManyRedirects,
        ) as e:
            logging.error("%s for HTTPS request to %s", e, domain_name)

    if http:
        try:
            response = requests.get("http://" + domain_name, timeout=http_timeout)
            if "NoSuchBucket" in response.text:
                return True

            if "Amazon CloudFront distribution is configured to block access from your country" in response.text:
                logging.error(
                    "Amazon CloudFront distribution for %s configured to block access from your country",
                    domain_name,
                )

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.TooManyRedirects,
        ) as e:
            logging.error("%s for HTTP request to %s", e, domain_name)

    return False


def get_bucket_name(domain_name, https=True, http=True, https_timeout=1, http_timeout=1):

    if https:
        try:
            response = requests.get("https://" + domain_name, timeout=https_timeout)
            if "<BucketName>" in response.text:
                bucket_info = re.search("<BucketName>(.*)</BucketName>", response.text)
                bucket_name = bucket_info.group(1)

                return bucket_name

            if "BucketName:" in response.text:
                bucket_info = re.search("BucketName: (.*)</li>", response.text)
                bucket_name = bucket_info.group(1)

                return bucket_name

        except (
            requests.exceptions.SSLError,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.TooManyRedirects,
        ):
            pass

    if http:
        try:
            response = requests.get("http://" + domain_name, timeout=http_timeout)
            if "<BucketName>" in response.text:
                bucket_info = re.search("<BucketName>(.*)</BucketName>", response.text)
                bucket_name = bucket_info.group(1)

                return bucket_name

            if "BucketName:" in response.text:
                bucket_info = re.search("BucketName: (.*)</li>", response.text)
                bucket_name = bucket_info.group(1)

                return bucket_name

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.TooManyRedirects,
        ):
            pass

    return None


def get_all_aws_ips():
    aws_url = "https://ip-ranges.amazonaws.com/ip-ranges.json"

    response = requests.get(aws_url, timeout=requests_timeout())
    prefixes = response.json()["prefixes"]

    filtered_prefixes = [p for p in prefixes if p["service"] == "EC2" or p["service"] == "GLOBALACCELERATOR"]
    return filtered_prefixes


def cloudfront_s3_fixed(domain):
    # determines if a CloudFront S3 vulnerability has been fixed
    try:
        response = requests.get(f"https://{domain}", timeout=requests_timeout())

        if response.status_code == 404 and "<Code>NotFound</Code>" in response.text:
            return False

    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return False

    return True
