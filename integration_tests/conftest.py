import pytest
from unittest.mock import patch
from integration_tests.manual_scans.cloudflare.mock.cloudflare_mock import CloudFlareMock


@pytest.fixture
def cloudflare_mock():
    with patch("CloudFlare.CloudFlare") as cf_mock:
        mock = CloudFlareMock()
        cf_mock.return_value = mock
        yield mock
