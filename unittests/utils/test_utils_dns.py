from unittest.mock import patch

import pytest
from assertpy import assert_that
from dns.resolver import NoAnswer
from dns.resolver import NoNameservers
from dns.resolver import NoResolverConfiguration
from dns.resolver import NXDOMAIN
from dns.resolver import Timeout

from utils.utils_dns import dns_deleted
from utils.utils_dns import firewall_test
from utils.utils_dns import updated_a_record
from utils.utils_dns import vulnerable_alias
from utils.utils_dns import vulnerable_cname
from utils.utils_dns import vulnerable_ns


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_ns_returns_false_when_query_name_does_not_exist(resolve_mock):
    resolve_mock.side_effect = NXDOMAIN

    result = vulnerable_ns("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_ns_returns_true_when_no_nameserver_for_A_or_NS_records(resolve_mock):
    resolve_mock.side_effect = [NoNameservers, NoNameservers]

    result = vulnerable_ns("google.com")

    assert_that(result).is_true()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_ns_returns_true_when_no_A_nameserver_and_0_NS_records(resolve_mock):
    resolve_mock.side_effect = [NoNameservers, []]

    result = vulnerable_ns("google.com")

    assert_that(result).is_true()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_ns_returns_false_when_no_answer(resolve_mock):
    resolve_mock.side_effect = NoAnswer

    result = vulnerable_ns("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_ns_returns_false_on_timeout(resolve_mock):
    resolve_mock.side_effect = Timeout

    result = vulnerable_ns("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_ns_returns_true_on_timeout_if_update_scan(resolve_mock):
    resolve_mock.side_effect = Timeout

    result = vulnerable_ns("google.com", True)

    assert_that(result).is_true()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_ns_returns_false_on_exception(resolve_mock):
    resolve_mock.side_effect = Exception

    result = vulnerable_ns("google.com")

    assert_that(result).is_false()


@patch("builtins.print")
@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_ns_prints_message_on_exception(resolve_mock, print_mock):
    e = Exception("Exception message")
    resolve_mock.side_effect = e
    expected_message = f"Unhandled exception testing DNS for NS records during standard scan: {e.args[0]}"

    _ = vulnerable_ns("google.com")

    print_mock.assert_called_with(expected_message)


@patch("builtins.print")
@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_ns_prints_message_on_exception_if_update_scan(resolve_mock, print_mock):
    e = Exception("Exception message")
    resolve_mock.side_effect = e
    expected_message = f"Unhandled exception testing DNS for NS records during update scan: {e.args[0]}"

    _ = vulnerable_ns("google.com", True)

    print_mock.assert_called_with(expected_message)


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_cname_returns_false_when_a_record_exists(resolve_mock):
    resolve_mock.side_effect = "<dns.resolver.Answer object at 0x110e56b80>"

    result = vulnerable_cname("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_cname_returns_true_when_cname_exists_but_no_a_record(resolve_mock):
    resolve_mock.side_effect = [NXDOMAIN, "<dns.resolver.Answer object at 0x110e56b80>"]

    result = vulnerable_cname("google.com")

    assert_that(result).is_true()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_cname_returns_false_when_no_a_record_or_cname(resolve_mock):
    resolve_mock.side_effect = [NXDOMAIN, NoNameservers]

    result = vulnerable_cname("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_cname_returns_false_when_record_type_not_found(resolve_mock):
    resolve_mock.side_effect = NoAnswer

    result = vulnerable_cname("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_cname_returns_false_when_no_nameservers(resolve_mock):
    resolve_mock.side_effect = NoNameservers

    result = vulnerable_cname("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_cname_returns_false_when_timeout(resolve_mock):
    resolve_mock.side_effect = Timeout

    result = vulnerable_cname("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_cname_update_scan_returns_true_when_timeout(resolve_mock):
    resolve_mock.side_effect = Timeout

    result = vulnerable_cname("google.com", True)

    assert_that(result).is_true()


@patch("builtins.print")
@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_cname_prints_message_on_exception(resolve_mock, print_mock):
    e = Exception("Exception message")
    resolve_mock.side_effect = e
    expected_message = f"Unhandled exception testing DNS for CNAME records during standard scan: {e.args[0]}"

    _ = vulnerable_cname("google.com")

    print_mock.assert_called_with(expected_message)


@patch("builtins.print")
@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_cname_prints_message_on_exception_when_update_scan_is_true(resolve_mock, print_mock):
    e = Exception("Exception message")
    resolve_mock.side_effect = e
    expected_message = f"Unhandled exception testing DNS for CNAME records during update scan: {e.args[0]}"

    _ = vulnerable_cname("google.com", True)

    print_mock.assert_called_with(expected_message)


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_alias_returns_false_when_a_record_exists(resolve_mock):
    resolve_mock.side_effect = "<dns.resolver.Answer object at 0x110e56b80>"

    result = vulnerable_alias("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_alias_returns_true_when_alias_does_not_resolve(resolve_mock):
    resolve_mock.side_effect = NoAnswer

    result = vulnerable_alias("google.com")

    assert_that(result).is_true()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_alias_returns_false_when_no_nameservers(resolve_mock):
    resolve_mock.side_effect = NoNameservers

    result = vulnerable_alias("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_alias_returns_false_when_timeout(resolve_mock):
    resolve_mock.side_effect = Timeout

    result = vulnerable_alias("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.Resolver.resolve")
def test_vulnerable_alias_update_scan_returns_true_when_timeout(resolve_mock):
    resolve_mock.side_effect = Timeout

    result = vulnerable_alias("google.com", True)

    assert_that(result).is_true()


@patch("dns.resolver.Resolver.resolve")
def test_dns_deleted_returns_false_when_record_type_not_found_for_query_name(resolve_mock):
    resolve_mock.side_effect = NoAnswer

    result = dns_deleted("google.com")

    assert_that(result).is_true()


@patch("dns.resolver.Resolver.resolve")
def test_dns_deleted_returns_false_when_query_name_does_not_exist(resolve_mock):
    resolve_mock.side_effect = NXDOMAIN

    result = dns_deleted("google.com")

    assert_that(result).is_true()


@patch("dns.resolver.Resolver.resolve")
def test_dns_deleted_returns_false_when_no_nameservers(resolve_mock):
    resolve_mock.side_effect = NoNameservers

    result = dns_deleted("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.Resolver.resolve")
def test_dns_deleted_returns_false_when_no_resolver_configuration(resolve_mock):
    resolve_mock.side_effect = NoResolverConfiguration

    result = dns_deleted("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.Resolver.resolve")
def test_dns_deleted_returns_false_when_timeout(resolve_mock):
    resolve_mock.side_effect = Timeout

    result = dns_deleted("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.Resolver.resolve")
def test_dns_deleted_returns_false_when_query_name_exists(resolve_mock):
    resolve_mock.side_effect = [["some result"]]

    result = dns_deleted("google.com")

    assert_that(result).is_false()


@patch("dns.resolver.Resolver.resolve")
def test_updated_a_record_returns_original_ip_when_record_type_not_found_for_query_name(resolve_mock):
    resolve_mock.side_effect = NoAnswer
    result = updated_a_record("google.com", "1.2.3.4")
    expected = "1.2.3.4"

    assert_that(result).is_equal_to(expected)


@patch("dns.resolver.Resolver.resolve")
def test_updated_a_record_returns_original_ip_when_query_name_does_not_exist(resolve_mock):
    resolve_mock.side_effect = NXDOMAIN
    result = updated_a_record("google.com", "1.2.3.4")
    expected = "1.2.3.4"

    assert_that(result).is_equal_to(expected)


@patch("dns.resolver.Resolver.resolve")
def test_updated_a_record_returns_original_ip_when_no_nameservers(resolve_mock):
    resolve_mock.side_effect = NoNameservers
    result = updated_a_record("google.com", "1.2.3.4")
    expected = "1.2.3.4"

    assert_that(result).is_equal_to(expected)


@patch("dns.resolver.Resolver.resolve")
def test_updated_a_record_returns_original_ip_when_no_resolver_configuration(resolve_mock):
    resolve_mock.side_effect = NoResolverConfiguration
    result = updated_a_record("google.com", "1.2.3.4")
    expected = "1.2.3.4"

    assert_that(result).is_equal_to(expected)


@patch("dns.resolver.Resolver.resolve")
def test_updated_a_record_returns_original_ip_when_timeout(resolve_mock):
    resolve_mock.side_effect = Timeout
    result = updated_a_record("google.com", "1.2.3.4")
    expected = "1.2.3.4"

    assert_that(result).is_equal_to(expected)


@patch("dns.resolver.Resolver.resolve")
def test_firewall_test_exits_with_dns_timeout(resolve_mock):
    resolve_mock.side_effect = Timeout
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        firewall_test()
    assert_that(pytest_wrapped_e.type).is_equal_to(SystemExit)


@patch("dns.resolver.Resolver.resolve")
def test_firewall_test_exits_with_dns_noanswer(resolve_mock):
    resolve_mock.side_effect = NoAnswer
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        firewall_test()
    assert_that(pytest_wrapped_e.type).is_equal_to(SystemExit)
