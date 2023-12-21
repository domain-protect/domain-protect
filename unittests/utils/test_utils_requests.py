from assertpy import assert_that

from utils.utils_requests import cloudfront_s3_fixed


def test_cloudfront_s3_fixed(requests_mock):
    requests_mock.get(
        "https://example.com",
        text="some text",
        status_code=200,
    )

    result = cloudfront_s3_fixed("example.com")

    assert_that(result).is_true()


def test_cloudfront_s3_not_fixed(requests_mock):
    requests_mock.get(
        "https://example.com",
        text="<Code>NotFound</Code>",
        status_code=404,
    )

    result = cloudfront_s3_fixed("example.com")

    assert_that(result).is_false()
