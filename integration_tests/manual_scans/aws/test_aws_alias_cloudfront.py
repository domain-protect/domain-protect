from unittest.mock import call
from unittest.mock import patch

import requests
from common import setup_hosted_zone

from manual_scans.aws.aws_alias_cloudfront_s3 import main


@patch("manual_scans.aws.aws_alias_cloudfront_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_detects_vulnerable_domains(arg_parse_mock, print_list_mock, moto_route53, requests_mock):
    setup_hosted_zone(moto_route53, "abcd.cloudfront.net")

    requests_mock.get("https://vulnerable.domain-protect.com.", status_code=404, text="<Code>NotFound</Code>")

    main()

    print_list_mock.assert_has_calls(
        [
            call(["vulnerable.domain-protect.com."], "INSECURE_WS"),
            call(["abcd.cloudfront.net"], "OUTPUT_WS"),
        ],
    )


@patch("manual_scans.aws.aws_alias_cloudfront_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_ignores_non_vulnerable_domains(arg_parse_mock, print_list_mock, moto_route53, requests_mock):
    setup_hosted_zone(moto_route53, "abcd.cloudfront.net")

    requests_mock.get("https://vulnerable.domain-protect.com.", status_code=200, text="All good here")

    main()

    print_list_mock.assert_not_called()


@patch("manual_scans.aws.aws_alias_cloudfront_s3.print_list")
@patch("argparse.ArgumentParser")
def test_main_ignores_domains_with_connection_error(arg_parse_mock, print_list_mock, moto_route53, requests_mock):
    setup_hosted_zone(moto_route53, "abcd.cloudfront.net")

    requests_mock.get("https://vulnerable.domain-protect.com.", exc=requests.exceptions.ConnectionError)

    main()

    print_list_mock.assert_not_called()
