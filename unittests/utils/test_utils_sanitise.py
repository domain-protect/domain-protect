from utils.utils_sanitise import sanitise_wildcards
from assertpy import assert_that


def test_wildcard_replaced_by_random_string():
    input = {'Name': '\\052.wildcard.celidor.io.', 'Type': 'CNAME', 'TTL': 300, 'ResourceRecords': [{'Value': 'neverssl.com'}]}
    result = sanitise_wildcards(input)
    prefix = result["Name"].split(".")[0]

    assert_that(len(prefix)).is_equal_to(19)
