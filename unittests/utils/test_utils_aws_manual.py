import unittest
from unittest.mock import patch

from utils.utils_aws_manual import bucket_does_not_exist
from utils.utils_aws_manual import is_s3_bucket_url
from utils.utils_aws_manual import is_s3_website_endpoint_url


class TestS3BucketURLs(unittest.TestCase):
    def test_not_bucket_url(self):
        self.assertFalse(is_s3_bucket_url("example.com"))

    def test_direct_bucket_url(self):
        self.assertTrue(is_s3_bucket_url("bucket.s3.amazonaws.com"))

    def test_direct_regional_bucket_url(self):
        self.assertTrue(is_s3_bucket_url("bucket.s3.us-east-1.amazonaws.com"))

    def test_none_empty(self):
        self.assertFalse(is_s3_bucket_url(None))
        self.assertFalse(is_s3_bucket_url(""))


class TestS3WebsiteURLs(unittest.TestCase):
    def test_not_bucket_url(self):
        self.assertFalse(is_s3_website_endpoint_url("example.com"))

    # per https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteEndpoints.html
    # can have a dot or a dash separating the region
    def test_website_url_dash(self):
        self.assertTrue(is_s3_website_endpoint_url("bucket.s3-website-us-east-1.amazonaws.com"))

    def test_website_url_dot(self):
        self.assertTrue(is_s3_website_endpoint_url("bucket.s3-website.us-east-1.amazonaws.com"))

    def test_none_empty(self):
        self.assertFalse(is_s3_website_endpoint_url(None))
        self.assertFalse(is_s3_website_endpoint_url(""))


# helper class to hold a generic object
class Object:
    def __init__(self, **kwargs):
        self.attrs = kwargs

    def __getattr__(self, key):
        return self.attrs[key]


class TestS3ExistenceChecks(unittest.TestCase):
    @patch("requests.get", return_value=Object(status_code=200, text="hello"))
    def test_bucket_exists(self, requests_mock):
        self.assertFalse(bucket_does_not_exist("bucket.s3.amazonaws.com"))
        self.assertTrue(requests_mock.call_args.args[0] == "https://bucket.s3.amazonaws.com")

    BUCKET_DOES_NOT_EXIST_RESPONSE = "<Error><Code>NoSuchBucket</Code><Message>The specified bucket does not exist</Message><BucketName>bucket</BucketName><RequestId>X</RequestId><HostId>X</HostId></Error>"

    @patch("requests.get", return_value=Object(status_code=404, text=BUCKET_DOES_NOT_EXIST_RESPONSE))
    def test_bucket_does_not_exist(self, requests_mock):
        self.assertTrue(bucket_does_not_exist("bucket.s3.amazonaws.com"))
        self.assertTrue(requests_mock.call_args.args[0] == "https://bucket.s3.amazonaws.com")

    BUCKET_DOES_NOT_EXIST_RESPONSE_WEBSITE = """
        <html>
        <head><title>404 Not Found</title></head>
        <body>
        <h1>404 Not Found</h1>
        <ul>
        <li>Code: NoSuchBucket</li>
        <li>Message: The specified bucket does not exist</li>
        <li>BucketName: idontexistatall</li>
        <li>RequestId: X</li>
        <li>HostId: X</li>
        </ul>
        <hr/>
        </body>
        </html>
    """

    @patch("requests.get", return_value=Object(status_code=404, text=BUCKET_DOES_NOT_EXIST_RESPONSE_WEBSITE))
    def test_bucket_does_not_exist_website_endpoint_url(self, requests_mock):
        self.assertTrue(bucket_does_not_exist("bucket.s3-website-us-east-1.amazonaws.com"))
        self.assertTrue(requests_mock.call_args.args[0] == "https://bucket.s3-website-us-east-1.amazonaws.com")
