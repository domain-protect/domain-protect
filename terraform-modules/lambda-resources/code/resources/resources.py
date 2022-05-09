import json
import os
import boto3

project = os.environ["PROJECT"]
sns_topic_arn = os.environ["SNS_TOPIC_ARN"]


def list_stacks(region):
    session = boto3.Session(region_name=region)
    cloudformation = session.client("cloudformation")
    live_stacks = cloudformation.list_stacks(StackStatusFilter=["CREATE_COMPLETE"])["StackSummaries"]

    stacks = [c for c in live_stacks if c["StackName"].startswith(project + "-")]

    stack_names = []

    for stack in stacks:
        stack_names.append(stack["StackName"])

    return stack_names


def get_tags(region, stack_name):
    session = boto3.Session(region_name=region)
    cloudformation = session.client("cloudformation")

    tags = cloudformation.describe_stacks(StackName=stack_name)["Stacks"][0]["Tags"]

    return tags


def get_region_names():
    ec2 = boto3.client("ec2")
    regions = ec2.describe_regions()["Regions"]
    region_names = []
    for region in regions:
        region_name = region["RegionName"]
        region_names.append(region_name)

    return region_names


def get_account_name():
    # gets account alias, and if none is set, returns the account ID

    session = boto3.Session()
    iam = session.client("iam")

    response = iam.list_account_aliases()

    if len(response["AccountAliases"]) > 0:
        account_name = response["AccountAliases"][0]

        return account_name

    sts = session.client("sts")
    account_id = sts.get_caller_identity()["Account"]

    return account_id


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

    resources_json = {"Resources": []}
    regions = get_region_names()
    all_stacks = []

    for region in regions:
        stacks = list_stacks(region)

        for stack in stacks:
            tags = get_tags(region, stack)
            all_stacks.append(stack)
            resources_json["Resources"].append(tags)

    if len(all_stacks) > 0:
        publish_to_sns(resources_json, f"Resources in {get_account_name()} AWS account")
