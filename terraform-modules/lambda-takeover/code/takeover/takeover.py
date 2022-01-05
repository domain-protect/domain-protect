import json
import time
import os
import boto3
import requests

project = os.environ["PROJECT"]
sns_topic_arn = os.environ["SNS_TOPIC_ARN"]


def create_stack(region, template, takeover_domain, vulnerable_domain, account):

    session = boto3.Session(region_name=region)
    cloudformation = session.client("cloudformation")

    sanitised_domain = vulnerable_domain.replace(".", "-")

    stack_name = f"{project}-{sanitised_domain}"

    if "elasticbeanstalk" in takeover_domain:
        resource_type = "Elastic Beanstalk instance"

    else:
        resource_type = "S3 bucket"

    print(f"creating CloudFormation stack {vulnerable_domain} in {region} region")

    with open(template, "r", encoding="utf-8") as f:
        template = f.read()

        cloudformation.create_stack(
            StackName=stack_name,
            TemplateBody=template,
            Parameters=[{"ParameterKey": "DomainName", "ParameterValue": takeover_domain}],
            NotificationARNs=[],
            Capabilities=["CAPABILITY_NAMED_IAM"],
            OnFailure="ROLLBACK",
            Tags=[
                {"Key": "ResourceName", "Value": takeover_domain},
                {"Key": "ResourceType", "Value": resource_type},
                {"Key": "TakeoverAccount", "Value": get_account_name()},
                {"Key": "VulnerableAccount", "Value": account},
                {"Key": "VulnerableDomain", "Value": vulnerable_domain},
            ],
        )

        timeout = time.time() + 300  # 5mins
        while time.time() < timeout:
            status = cloudformation.describe_stacks(StackName=stack_name)["Stacks"][0]["StackStatus"]
            if status == "CREATE_IN_PROGRESS":
                print("resource creation in progress")
                time.sleep(5)

            elif status == "CREATE_COMPLETE":
                print("resource creation complete")
                return None

        print("resource creation timed out")
        return None


def s3_upload(path, bucket, region):

    session = boto3.Session(region_name=region)
    s3 = session.client("s3")

    print(f"uploading content to {bucket} S3 bucket in {region} region")

    for file in os.listdir(path):
        if file.endswith(".html"):
            s3.upload_file(
                os.path.join(path, file),
                bucket,
                file,
                ExtraArgs={"ACL": "public-read", "ContentType": "text/html"},
            )
        else:
            with open(os.path.join(path, file), "rb") as data:
                s3.upload_fileobj(
                    data,
                    bucket,
                    file,
                    ExtraArgs={"ACL": "public-read", "ContentType": "text/html"},
                )


def s3_takeover(target, account):

    domain = target.rsplit(".", 4)[0]
    region = target.rsplit(".", 4)[2]

    print(f"Creating S3 bucket {domain} in {region} region")
    create_stack(region, "s3.yaml", domain, domain, account)
    s3_upload("content", domain, region)


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


def takeover_successful(domain_name):

    try:
        response = requests.get("http://" + domain_name, timeout=60)
        if "Domain Protect" in response.text:
            return True

    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        pass

    try:
        response = requests.get("https://" + domain_name, timeout=60)
        if "Domain Protect" in response.text:
            return True

    except (
        requests.exceptions.SSLError,
        requests.exceptions.ConnectionError,
        requests.exceptions.ReadTimeout,
    ):
        pass

    return False


def lambda_handler(event, context):  # pylint:disable=unused-argument

    message = event["Records"][0]["Sns"]["Message"]
    json_data = json.loads(message)
    notification_json = {"Takeovers": []}
    takeover_domains = []

    try:
        findings = json_data["Findings"]
        for finding in findings:
            print(
                f"Attempting takeover of {finding['Takeover']} for vulnerable domain {finding['Domain']} in {finding['Account']} AWS Account"
            )
            if ".s3-website." in finding["Takeover"]:
                s3_takeover(finding["Takeover"], finding["Account"])

                if takeover_successful(finding["Domain"]):
                    print(f"Takeover of {finding['Domain']} successful")
                    takeover_status = "success"

                else:
                    print(f"Takeover of {finding['Domain']} unsuccessful")
                    takeover_status = "failure"

                notification_json["Takeovers"].append(
                    {
                        "ResourceType": "S3 Bucket",
                        "TakeoverDomain": finding["Domain"],
                        "TakeoverAccount": get_account_name(),
                        "VulnerableDomain": finding["Domain"],
                        "VulnerableAccount": finding["Account"],
                        "TakeoverStatus": takeover_status,
                    }
                )

                takeover_domains.append(finding["Domain"])

        if len(takeover_domains) > 0:
            publish_to_sns(notification_json, "Hostile takeovers prevented")

    except KeyError:
        pass
