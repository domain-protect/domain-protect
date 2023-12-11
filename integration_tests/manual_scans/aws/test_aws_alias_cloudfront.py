from unittest.mock import call
from unittest.mock import patch

import requests
from common import setup_cloudfront_distribution_with_origin_url
from common import setup_hosted_zone_with_alias

from manual_scans.aws.aws_alias_cloudfront_s3 import main


@patch("manual_scans.aws.aws_alias_cloudfront_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_detects_vulnerable_domains(arg_parse_mock, print_list_mock, moto_route53, moto_cloudfront, requests_mock):
    cloudfront = setup_cloudfront_distribution_with_origin_url(moto_cloudfront, "my-bucket.s3.us-east-1.amazonaws.com")
    setup_hosted_zone_with_alias(moto_route53, cloudfront["DomainName"])

    requests_mock.get("https://vulnerable.domain-protect.com.", status_code=404, text="<Code>NotFound</Code>")
    requests_mock.get("https://my-bucket.s3.us-east-1.amazonaws.com", status_code=404, text="<Code>NoSuchBucket</Code>")

    main()

    print_list_mock.assert_has_calls(
        [
            call(["vulnerable.domain-protect.com."], "INSECURE_WS"),
            call([cloudfront["DomainName"]], "OUTPUT_WS"),
        ],
    )


@patch("manual_scans.aws.aws_alias_cloudfront_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_ignores_non_vulnerable_domains(
    arg_parse_mock,
    print_list_mock,
    moto_route53,
    moto_cloudfront,
    requests_mock,
):
    cloudfront = setup_cloudfront_distribution_with_origin_url(moto_cloudfront, "my-bucket.s3.us-east-1.amazonaws.com")
    setup_hosted_zone_with_alias(moto_route53, cloudfront["DomainName"])

    requests_mock.get("https://vulnerable.domain-protect.com.", status_code=200, text="All good here")

    main()

    print_list_mock.assert_not_called()


@patch("manual_scans.aws.aws_alias_cloudfront_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_ignores_non_vulnerable_domains_2(
    arg_parse_mock,
    print_list_mock,
    moto_route53,
    moto_cloudfront,
    requests_mock,
):
    cloudfront = setup_cloudfront_distribution_with_origin_url(moto_cloudfront, "my-bucket.s3.us-east-1.amazonaws.com")
    setup_hosted_zone_with_alias(moto_route53, cloudfront["DomainName"])

    requests_mock.get("https://vulnerable.domain-protect.com.", status_code=404, text="<Code>NotFound</Code>")
    requests_mock.get("https://my-bucket.s3.us-east-1.amazonaws.com", status_code=200, text="All good there")
    main()

    print_list_mock.assert_not_called()


@patch("manual_scans.aws.aws_alias_cloudfront_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_ignores_domains_with_non_s3_origins(
    arg_parse_mock,
    print_list_mock,
    moto_route53,
    moto_cloudfront,
    requests_mock,
):
    cloudfront = setup_cloudfront_distribution_with_origin_url(
        moto_cloudfront,
        "non-s3-origin.example.com",
        is_s3=False,
    )
    setup_hosted_zone_with_alias(moto_route53, cloudfront["DomainName"])

    requests_mock.get("https://vulnerable.domain-protect.com.", status_code=404, text="<Code>NotFound</Code>")

    main()

    print_list_mock.assert_not_called()


@patch("manual_scans.aws.aws_alias_cloudfront_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_no_cloudfront_distribution(arg_parse_mock, print_list_mock, moto_route53, moto_cloudfront, requests_mock):
    main()

    print_list_mock.assert_not_called()
    # Implicitly, we also assert no exception is raised
