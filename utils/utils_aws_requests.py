import requests

from utils.utils_aws import get_cloudfront_s3_origin_url
from utils.utils_aws_manual import bucket_does_not_exist
from utils.utils_aws_manual import is_s3_bucket_url
from utils.utils_aws_manual import is_s3_website_endpoint_url


def vulnerable_cloudfront_s3(account_id, account_name, domain):
    # determines if a CloudFront distribution is vulnerable due to S3 bucket not present
    try:
        response = requests.get(f"https://{domain}", timeout=1)

        if response.status_code == 404 and "<Code>NotFound</Code>" in response.text:
            bucket_url = get_cloudfront_s3_origin_url(account_id, account_name, domain)
            if not is_s3_bucket_url(bucket_url) and not is_s3_website_endpoint_url(bucket_url):
                return False

            return bucket_does_not_exist(bucket_url)

    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        pass

    return False
