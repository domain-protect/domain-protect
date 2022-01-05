import json
import os
import boto3

project = os.environ["PROJECT"]
sns_topic_arn = os.environ["SNS_TOPIC_ARN"]


def get_region_names():
    ec2 = boto3.client("ec2")
    regions = ec2.describe_regions()["Regions"]
    region_names = []
    for region in regions:
        region_name = region["RegionName"]
        region_names.append(region_name)

    return region_names


def get_account_name():

    session = boto3.Session()
    iam = session.client("iam")

    response = iam.list_account_aliases()
    account_name = response["AccountAliases"][0]

    return account_name


def publish_to_sns(json_data, subject):

    try:
        print(json.dumps(json_data, sort_keys=True, indent=2))
        client = boto3.client("sns")

        response = client.publish(
            TargetArn=sns_topic_arn,
            Subject=subject,
            Message=json.dumps({"default": json.dumps(json_data)}),
            MessageStructure="json",
        )
        print(response)

    except Exception:
        print(f"ERROR: Unable to publish to SNS topic {sns_topic_arn}")


def lambda_handler(event, context):  # pylint:disable=unused-argument

    regions = get_region_names()
    print(regions)

    account = get_account_name()
    print(account)