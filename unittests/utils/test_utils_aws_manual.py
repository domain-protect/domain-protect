import unittest

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
