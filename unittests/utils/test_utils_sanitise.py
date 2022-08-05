from utils.utils_sanitise import sanitise_wildcards, restore_wildcard, sanitise_domain
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
