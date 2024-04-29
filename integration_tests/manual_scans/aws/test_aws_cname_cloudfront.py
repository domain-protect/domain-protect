from unittest.mock import call
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import requests
from common import setup_cloudfront_distribution_with_origin_url
from common import setup_hosted_zone_with_cname

from manual_scans.aws.aws_cname_cloudfront_s3 import main


@patch("manual_scans.aws.aws_cname_cloudfront_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_detects_vulnerable_domains(
    arg_parse_mock,
    print_list_mock,
    moto_route53,
    moto_cloudfront,
    requests_mock,
    dns_mock,
):
    cloudfront = setup_cloudfront_distribution_with_origin_url(moto_cloudfront, "my-bucket.s3.us-east-1.amazonaws.com")
    setup_hosted_zone_with_cname(moto_route53, cloudfront["DomainName"])

    requests_mock.get("https://vulnerable.domain-protect.com.", status_code=404, text="<Code>NotFound</Code>")
    requests_mock.get("https://my-bucket.s3.us-east-1.amazonaws.com", status_code=404, text="<Code>NoSuchBucket</Code>")
    dns_mock.add_lookup("vulnerable.domain-protect.com.", cloudfront["DomainName"], record_type="CNAME")

    main()

    print_list_mock.assert_has_calls(
        [
            call(["vulnerable.domain-protect.com."], "INSECURE_WS"),
        ],
    )


@patch("manual_scans.aws.aws_cname_cloudfront_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_ignores_non_vulnerable_domains(
    arg_parse_mock,
    print_list_mock,
    dns_mock,
    moto_route53,
    moto_cloudfront,
    requests_mock,
):
    cloudfront = setup_cloudfront_distribution_with_origin_url(moto_cloudfront, "my-bucket.s3.us-east-1.amazonaws.com")
    setup_hosted_zone_with_cname(moto_route53, cloudfront["DomainName"])

    requests_mock.get("https://vulnerable.domain-protect.com.", status_code=200, text="All good here")

    main()

    print_list_mock.assert_not_called()


@patch("utils.utils_dns.firewall_test")
@patch("manual_scans.aws.aws_cname_cloudfront_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_ignores_non_vulnerable_domains_2(
    arg_parse_mock,
    print_list_mock,
    dns_mock,
    moto_route53,
    moto_cloudfront,
    requests_mock,
):
    cloudfront = setup_cloudfront_distribution_with_origin_url(moto_cloudfront, "my-bucket.s3.us-east-1.amazonaws.com")
    setup_hosted_zone_with_cname(moto_route53, cloudfront["DomainName"])

    requests_mock.get("https://vulnerable.domain-protect.com.", status_code=404, text="<Code>NotFound</Code>")
    requests_mock.get("https://my-bucket.s3.us-east-1.amazonaws.com", status_code=200, text="All good there")

    main()

    print_list_mock.assert_not_called()


@patch("utils.utils_dns.firewall_test")
@patch("manual_scans.aws.aws_cname_cloudfront_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_ignores_domains_with_connection_error(
    arg_parse_mock,
    print_list_mock,
    dns_mock,
    moto_route53,
    moto_cloudfront,
    requests_mock,
):
    cloudfront = setup_cloudfront_distribution_with_origin_url(moto_cloudfront, "my-bucket.s3.us-east-1.amazonaws.com")
    setup_hosted_zone_with_cname(moto_route53, cloudfront["DomainName"])

    requests_mock.get("https://vulnerable.domain-protect.com.", exc=requests.exceptions.ConnectionError)

    main()

    print_list_mock.assert_not_called()


@patch("utils.utils_dns.firewall_test")
@patch("manual_scans.aws.aws_cname_cloudfront_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_no_cloudfront_distribution(
    arg_parse_mock,
    print_list_mock,
    dns_mock,
    moto_route53,
    moto_cloudfront,
    requests_mock,
):
    main()

    print_list_mock.assert_not_called()
    # Implicitly, we also assert no exception is raised
