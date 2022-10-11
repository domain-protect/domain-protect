import json

from utils.utils_sanitise import sanitise_wildcards, restore_wildcard, sanitise_domain, filtered_ns_records
from assertpy import assert_that


def test_wildcard_replaced_by_random_string():
    input_dict = {
        "Name": "\\052.wildcard.celidor.io.",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "neverssl.com"}],
    }
    result = sanitise_wildcards(input_dict)
    prefix = result["Name"].split(".")[0]

    assert_that(prefix).is_length(19)


def test_wildcard_restored():
    domain = "uf7gh39sws-wildcard.example.com"
    expected = "*.example.com"
    result = restore_wildcard(domain)

    assert_that(result).is_equal_to(expected)


def test_domain_without_wildcard_unchanged():
    domain = "myapp.example.com"
    result = restore_wildcard(domain)

    assert_that(result).is_equal_to(domain)


def test_wildcard_domain_sanitised():
    domain = "*.example.com"
    result = sanitise_domain(domain)
    prefix = result.split(".")[0]

    assert_that(prefix).is_length(19)


def test_ordinary_domain_unchanged():
    domain = "myapp.example.com"
    result = sanitise_domain(domain)

    assert_that(result).is_equal_to(domain)


def test_standard_ns_record_not_filtered():

    records = [
        {"Name": "sub.example.com", "Type": "NS", "TTL": 300, "ResourceRecords": [{"Value": "ns1.awsdns-89.com"}]}
    ]

    expected = [
        {"Name": "sub.example.com", "Type": "NS", "TTL": 300, "ResourceRecords": [{"Value": "ns1.awsdns-89.com"}]}
    ]

    result = filtered_ns_records(records, "example.com")

    assert_that(result).is_equal_to(expected)


def test_ns_record_same_as_hosted_zone_excluded():

    records = [{"Name": "example.com", "Type": "NS", "TTL": 300, "ResourceRecords": [{"Value": "ns1.awsdns-89.com"}]}]

    expected = []
    result = filtered_ns_records(records, "example.com")

    assert_that(result).is_equal_to(expected)


def test_ns_record_starting_with_underscore_excluded():

    records = [
        {
            "Name": "_mta-sts.example.com",
            "Type": "NS",
            "TTL": 300,
            "ResourceRecords": [{"Value": "ns-dkim.ondmarc.com"}],
        }
    ]

    expected = []
    result = filtered_ns_records(records, "example.com")

    assert_that(result).is_equal_to(expected)
