from unittest.mock import patch
from assertpy import assert_that
from unittests.utils.test_utils import load_json
from utils.utils_hackerone import hackerone_get_program_handle, hackerone_create_report

hackerone_base_url = "https://api.hackerone.com/v1/"


def os_environ_hackerone_side_effect(key, default=None):
    env_vars = {"HACKERONE_API_TOKEN": "test-token", "PROJECT": "domain-protect"}
    return env_vars.get(key, default)


@patch("os.environ")
def test_hackerone_get_program_handle(os_environ_mock, requests_mock):

    os_environ_mock.get.side_effect = os_environ_hackerone_side_effect
    org_json = load_json("unittests/captures/hackerone-program.json")

    requests_mock.get(
        hackerone_base_url + "me/programs",
        json=org_json,
        status_code=200,
    )

    expected = "owasp_sandbox_2_h1b"
    result = hackerone_get_program_handle()

    assert_that(requests_mock.request_history).is_length(1)
    assert_that(requests_mock.last_request.method).is_equal_to("GET")
    assert_that(result).is_equal_to(expected)


@patch("os.environ")
def test_hackerone_create_report(os_environ_mock, requests_mock, capfd):

    os_environ_mock.get.side_effect = os_environ_hackerone_side_effect
    org_json = load_json("unittests/captures/hackerone-program.json")
    report_json = load_json("unittests/captures/hackerone-report.json")

    requests_mock.get(
        hackerone_base_url + "me/programs",
        json=org_json,
        status_code=200,
    )

    requests_mock.post(hackerone_base_url + "reports", status_code=201, json=report_json)

    hackerone_create_report("test.example.com", "hosted zone", "NS")

    assert_that(requests_mock.request_history).is_length(2)
    assert_that(requests_mock.last_request.method).is_equal_to("POST")

    out, err = capfd.readouterr()
    print(err)
    assert_that(out).contains("created")


@patch("os.environ")
def test_hackerone_create_report_fails(os_environ_mock, requests_mock, capfd):

    os_environ_mock.get.side_effect = os_environ_hackerone_side_effect
    org_json = load_json("unittests/captures/hackerone-program.json")
    not_found_json = load_json("unittests/captures/hackerone-not-found.json")

    requests_mock.get(
        hackerone_base_url + "me/programs",
        json=org_json,
        status_code=200,
    )

    requests_mock.post(hackerone_base_url + "reports", status_code=404, json=not_found_json)

    hackerone_create_report("test.example.com", "hosted zone", "NS")

    assert_that(requests_mock.request_history).is_length(2)
    assert_that(requests_mock.last_request.method).is_equal_to("POST")

    out, err = capfd.readouterr()
    print(err)
    assert_that(out).contains("failed")
