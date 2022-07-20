from pathlib import Path
import pytest
import os
import boto3
from unittest.mock import patch
from integration_tests.mocks.cloudflare_mock import CloudFlareMock
from integration_tests.mocks.dns_mock import DNSMock
from moto import mock_route53


@pytest.fixture
def cloudflare_mock():
    with patch("CloudFlare.CloudFlare") as cf_mock:
        mock = CloudFlareMock()
        cf_mock.return_value = mock
        yield mock


@pytest.fixture
def dns_mock():
    with patch("dns.resolver.resolve") as monkey_patch:
        mock = DNSMock(monkey_patch)
        monkey_patch.side_effect = mock.generate_lookup_function()
        yield mock


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    moto_credentials_file_path = Path(__file__).parent.absolute() / "dummy_aws_credentials"
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = str(moto_credentials_file_path)


# pylint: disable=unused-argument
@pytest.fixture(scope="function")
def moto_route53(aws_credentials):
    with mock_route53():
        yield boto3.client("route53", region_name="us-east-1")
