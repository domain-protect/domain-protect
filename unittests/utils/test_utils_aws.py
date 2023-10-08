from unittest.mock import patch

from assertpy import assert_that
from boto3 import Session

from utils.utils_aws import assume_role
from utils.utils_aws import create_session
from utils.utils_aws import generate_role_arn
from utils.utils_aws import generate_temporary_credentials
from utils.utils_aws import eb_susceptible


def get_test_credentials():
    return {
        "Credentials": {
            "AccessKeyId": "test_access_key",
            "SecretAccessKey": "test_secret_access_key",
            "SessionToken": "test_session_token",
        },
    }


def test_generate_role_arn_puts_account_in_correct_place():
    account = "test_account"
    expected_arn_start = f"arn:aws:iam::{account}"

    result = generate_role_arn(account, "test_role")

    assert_that(result).starts_with(expected_arn_start)


def test_generate_role_arn_puts_role_at_the_end():
    role = "test_role"
    expected_arn_end = f":role/{role}"

    result = generate_role_arn("test_account", role)

    assert_that(result).ends_with(expected_arn_end)


@patch("boto3.client")
def test_generate_temporary_credentials_calls_assume_role_with_correct_arn_and_project(boto3_client_mock):
    account = "test_account"
    role_name = "test_role"
    external_id = ""
    project = "test_project"

    expected_arn = generate_role_arn(account, role_name)

    _ = generate_temporary_credentials(account, role_name, external_id, project)

    boto3_client_mock().assume_role.assert_called_once_with(RoleArn=expected_arn, RoleSessionName=project)


@patch("boto3.client")
def test_generate_temporary_credentials_calls_assume_role_with_correct_external_id_when_passed(boto3_client_mock):
    account = "test_account"
    role_name = "test_role"
    external_id = "test_external_id"
    project = "test_project"

    expected_arn = generate_role_arn(account, role_name)

    _ = generate_temporary_credentials(account, role_name, external_id, project)

    boto3_client_mock().assume_role.assert_called_once_with(
        RoleArn=expected_arn,
        RoleSessionName=project,
        ExternalId=external_id,
    )


# pylint: disable=unused-argument
@patch("boto3.client")
@patch("builtins.print")
def test_generate_temporary_credentials_prints_message_with_role_name_and_account(print_mock, boto3_client_mock):
    account = "test_account"
    role_name = "test_role"
    external_id = ""
    project = "test_project"

    _ = generate_temporary_credentials(account, role_name, external_id, project)

    print_mock.assert_called_once_with(f"Assumed {role_name} role in account {account}")


@patch("boto3.client")
def test_generate_temporary_credentials_returns_value_from_assume_role(boto3_client_mock):
    account = "test_account"
    role_name = "test_role"
    external_id = "test_external_id"
    project = "test_project"

    expected_temp_credentials = get_test_credentials()

    boto3_client_mock().assume_role.return_value = expected_temp_credentials

    result = generate_temporary_credentials(account, role_name, external_id, project)

    assert_that(result).is_equal_to(expected_temp_credentials)


@patch("boto3.session")
@patch("os.environ")
def test_create_session_passes_correct_credentials_and_region_when_no_override_passed(
    os_environ_mock,
    boto3_session_mock,
):
    expected_temp_credentials = get_test_credentials()["Credentials"]
    expected_region = "test_region"

    os_environ_mock.__getitem__.side_effect = {"AWS_REGION": expected_region}.__getitem__

    _ = create_session(expected_temp_credentials, "None")

    boto3_session_mock.Session.assert_called_once_with(
        aws_access_key_id=expected_temp_credentials["AccessKeyId"],
        aws_secret_access_key=expected_temp_credentials["SecretAccessKey"],
        aws_session_token=expected_temp_credentials["SessionToken"],
        region_name=expected_region,
    )


@patch("boto3.session")
def test_create_session_passes_correct_credentials_and_region_override_is_passed(boto3_session_mock):
    expected_temp_credentials = get_test_credentials()["Credentials"]
    expected_region = "test_region_override"

    _ = create_session(expected_temp_credentials, expected_region)

    boto3_session_mock.Session.assert_called_once_with(
        aws_access_key_id=expected_temp_credentials["AccessKeyId"],
        aws_secret_access_key=expected_temp_credentials["SecretAccessKey"],
        aws_session_token=expected_temp_credentials["SessionToken"],
        region_name=expected_region,
    )


def test_create_session_returns_the_session_object():
    expected_temp_credentials = get_test_credentials()["Credentials"]
    expected_region = "test_region_override"
    expected_session = Session(
        aws_access_key_id=expected_temp_credentials["AccessKeyId"],
        aws_secret_access_key=expected_temp_credentials["SecretAccessKey"],
        aws_session_token=expected_temp_credentials["SessionToken"],
        region_name=expected_region,
    )

    result = create_session(expected_temp_credentials, expected_region)

    assert_that(result.get_credentials().access_key).is_equal_to(expected_session.get_credentials().access_key)
    assert_that(result.get_credentials().secret_key).is_equal_to(expected_session.get_credentials().secret_key)
    assert_that(result.get_credentials().token).is_equal_to(expected_session.get_credentials().token)
    assert_that(result.region_name).is_equal_to(expected_session.region_name)


@patch("utils.utils_aws.create_session")
@patch("utils.utils_aws.generate_temporary_credentials")
@patch("os.environ")
def test_assume_role_returns_session_object(os_environ_mock, generate_temp_credentials_mock, create_session_mock):
    env_vars = {
        "AWS_REGION": "test_region",
        "PROJECT": "test_project",
        "SECURITY_AUDIT_ROLE_NAME": "test_role",
        "EXTERNAL_ID": "test_external_id",
    }
    expected_temp_credentials = get_test_credentials()
    expected_session = Session(
        aws_access_key_id=expected_temp_credentials["Credentials"]["AccessKeyId"],
        aws_secret_access_key=expected_temp_credentials["Credentials"]["SecretAccessKey"],
        aws_session_token=expected_temp_credentials["Credentials"]["SessionToken"],
        region_name="test_region",
    )

    os_environ_mock.__getitem__.side_effect = env_vars.__getitem__
    generate_temp_credentials_mock.return_value = expected_temp_credentials
    create_session_mock.return_value = expected_session

    result = assume_role("some_account")

    assert_that(result.get_credentials().access_key).is_equal_to(expected_session.get_credentials().access_key)
    assert_that(result.get_credentials().secret_key).is_equal_to(expected_session.get_credentials().secret_key)
    assert_that(result.get_credentials().token).is_equal_to(expected_session.get_credentials().token)
    assert_that(result.region_name).is_equal_to(expected_session.region_name)


@patch("utils.utils_aws.generate_temporary_credentials")
@patch("os.environ")
def test_assume_role_returns_none_on_exception(os_environ_mock, generate_temp_credentials_mock):
    env_vars = {
        "AWS_REGION": "test_region",
        "PROJECT": "test_project",
        "SECURITY_AUDIT_ROLE_NAME": "test_role",
        "EXTERNAL_ID": "test_external_id",
    }

    os_environ_mock.__getitem__.side_effect = env_vars.__getitem__
    generate_temp_credentials_mock.side_effect = Exception("test")

    result = assume_role("some_account")

    assert_that(result).is_none()


@patch("logging.exception")
@patch("utils.utils_aws.generate_temporary_credentials")
@patch("os.environ")
def test_assume_role_logs_message_on_exception(os_environ_mock, generate_temp_credentials_mock, log_mock):
    env_vars = {
        "AWS_REGION": "test_region",
        "PROJECT": "test_project",
        "SECURITY_AUDIT_ROLE_NAME": "test_role",
        "EXTERNAL_ID": "test_external_id",
    }

    os_environ_mock.__getitem__.side_effect = env_vars.__getitem__
    generate_temp_credentials_mock.side_effect = Exception("test")

    _ = assume_role("some_account")

    log_mock.assert_called_once_with("ERROR: Failed to assume test_role role in AWS account some_account")


def test_eb_susceptible_returns_true_with_user_chosen_name():
    result = eb_susceptible("myapp.eu-west-1.elasticbeanstalk.com")

    assert_that(result).is_true()


def test_eb_susceptible_returns_true_with_domain_ending_in_period():
    result = eb_susceptible("myapp.eu-west-1.elasticbeanstalk.com.")

    assert_that(result).is_true()


def test_eb_susceptible_returns_true_with_auto_generated_name():
    result = eb_susceptible("myapp.7890hw48u596.eu-west-1.elasticbeanstalk.com")

    assert_that(result).is_false()


def test_eb_susceptible_returns_false_with_reserved_prefix():
    result = eb_susceptible("eba-myapp.eu-west-1.elasticbeanstalk.com")

    assert_that(result).is_false()


def test_eb_susceptible_returns_false_with_non_eb_domain():
    result = eb_susceptible("eba-myapp.eu-west-1.azurewebsites.net")

    assert_that(result).is_false()
