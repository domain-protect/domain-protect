import unittest

from utils.utils_aws_manual import is_s3_bucket_url

class TestIsS3BucketURL(unittest.TestCase):
  def test_not_bucket_url(self):
    self.assertFalse(is_s3_bucket_url("example.com"))
    
  def test_direct_bucket_url(self):
    self.assertTrue(is_s3_bucket_url("bucket.s3.amazonaws.com"))
    
  def test_direct_regional_bucket_url(self):
    self.assertTrue(is_s3_bucket_url("bucket.s3.us-east-1.amazonaws.com"))
    
  def test_none_empty(self):
    self.assertFalse(is_s3_bucket_url(None))
    self.assertFalse(is_s3_bucket_url(""))