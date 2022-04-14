import re
import requests


def vulnerable_storage(domain_name, https=True, http=True, https_timeout=1, http_timeout=1):

    if https:
        try:
            response = requests.get("https://" + domain_name, timeout=https_timeout)
            if "NoSuchBucket" in response.text:
                return True

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
            if "NoSuchBucket" in response.text:
                return True

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.TooManyRedirects,
        ):
            pass

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

    response = requests.get(aws_url)
    prefixes = response.json()["prefixes"]

    filtered_prefixes = [p for p in prefixes if p["service"] == "EC2" or p["service"] == "GLOBALACCELERATOR"]
    return filtered_prefixes
