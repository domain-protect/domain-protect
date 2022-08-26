from utils.utils_dns import vulnerable_ns, dns_deleted
from unittest.mock import patch
from assertpy import assert_that
from dns.resolver import NXDOMAIN, NoNameservers, NoAnswer, NoResolverConfiguration, Timeout


@patch("dns.resolver.resolve")
def test_vulnerable_ns_returns_false_when_query_name_does_not_exist(resolve_mock):
    resolve_mock.side_effect = NXDOMAIN

    result = vulnerable_ns("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.resolve")
def test_vulnerable_ns_returns_true_when_no_nameserver_for_A_or_NS_records(resolve_mock):
    resolve_mock.side_effect = [NoNameservers, NoNameservers]

    result = vulnerable_ns("google.com")

    assert_that(result).is_true()


@patch("dns.resolver.resolve")
def test_vulnerable_ns_returns_true_when_no_A_nameserver_and_0_NS_records(resolve_mock):
    resolve_mock.side_effect = [NoNameservers, []]

    result = vulnerable_ns("google.com")

    assert_that(result).is_true()


@patch("dns.resolver.resolve")
def test_vulnerable_ns_returns_false_when_no_A_nameserver_and_1_NS_records(resolve_mock):
    resolve_mock.side_effect = [NoNameservers, ["some result"]]

    result = vulnerable_ns("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.resolve")
def test_vulnerable_ns_returns_false_when_no_answer(resolve_mock):
    resolve_mock.side_effect = NoAnswer

    result = vulnerable_ns("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.resolve")
def test_vulnerable_ns_returns_false_on_timeout(resolve_mock):
    resolve_mock.side_effect = Timeout

    result = vulnerable_ns("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.resolve")
def test_vulnerable_ns_returns_true_on_timeout_if_update_scan_is_true(resolve_mock):
    resolve_mock.side_effect = Timeout

    result = vulnerable_ns("google.com", True)

    assert_that(result).is_true()


@patch("dns.resolver.resolve")
def test_vulnerable_ns_returns_false_on_exception(resolve_mock):
    resolve_mock.side_effect = Exception

    result = vulnerable_ns("google.com")

    assert_that(result).is_false()


@patch("builtins.print")
@patch("dns.resolver.resolve")
def test_vulnerable_ns_prints_message_on_exception(resolve_mock, print_mock):
    e = Exception("Exception message")
    resolve_mock.side_effect = e
    expected_message = f"Unhandled exception testing DNS for NS records during standard scan: {e.args[0]}"

    _ = vulnerable_ns("google.com")

    print_mock.assert_called_with(expected_message)


@patch("builtins.print")
@patch("dns.resolver.resolve")
def test_vulnerable_ns_prints_message_on_exception_when_update_scan_is_true(resolve_mock, print_mock):
    e = Exception("Exception message")
    resolve_mock.side_effect = e
    expected_message = f"Unhandled exception testing DNS for NS records during update scan: {e.args[0]}"

    _ = vulnerable_ns("google.com", True)

    print_mock.assert_called_with(expected_message)


@patch("dns.resolver.resolve")
def test_dns_deleted_returns_false_when_record_type_not_found_for_query_name(resolve_mock):
    resolve_mock.side_effect = NoAnswer

    result = dns_deleted("google.com")

    assert_that(result).is_true()


@patch("dns.resolver.resolve")
def test_dns_deleted_returns_false_when_query_name_does_not_exist(resolve_mock):
    resolve_mock.side_effect = NXDOMAIN

    result = dns_deleted("google.com")

    assert_that(result).is_true()


@patch("dns.resolver.resolve")
def test_dns_deleted_returns_false_when_no_nameservers(resolve_mock):
    resolve_mock.side_effect = NoNameservers

    result = dns_deleted("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.resolve")
def test_dns_deleted_returns_false_when_no_nameservers(resolve_mock):
    resolve_mock.side_effect = NoResolverConfiguration

    result = dns_deleted("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.resolve")
def test_dns_deleted_returns_false_when_timeout(resolve_mock):
    resolve_mock.side_effect = Timeout

    result = dns_deleted("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.resolve")
def test_dns_deleted_returns_false_when_query_name_exists(resolve_mock):
    resolve_mock.side_effect = [["some result"]]

    result = dns_deleted("google.com")

    assert_that(result).is_false()
