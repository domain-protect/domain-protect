import pytest
from unittest.mock import patch
from integration_tests.mocks.cloudflare_mock import CloudFlareMock
from integration_tests.mocks.dns_mock import DNSMock


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
