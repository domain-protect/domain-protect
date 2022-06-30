from utils.utils_dns import vulnerable_ns
from unittest.mock import patch
from assertpy import assert_that
from dns.resolver import NXDOMAIN


@patch("dns.resolver.resolve")
def test_vulnerable_ns_returns_false_when_NXDOMAIN_thrown(resolve_mock):
    resolve_mock.side_effect = NXDOMAIN

    result = vulnerable_ns("google.com")

    assert_that(result).is_false()
