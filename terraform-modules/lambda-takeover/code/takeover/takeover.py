import json
import time
import os
import boto3
import requests

from botocore import exceptions

project = os.environ["PROJECT"]
sns_topic_arn = os.environ["SNS_TOPIC_ARN"]
suffix = os.environ["SUFFIX"]


def create_stack(region, template, takeover_domain, vulnerable_domain, account):

    session = boto3.Session(region_name=region)
    cloudformation = session.client("cloudformation")

    sanitised_domain = vulnerable_domain.replace(".", "-")
    if sanitised_domain.endswith("-"):
        sanitised_domain = sanitised_domain[:-1]

    stack_name = f"{project}-{sanitised_domain}"[:128]  # max length of Stack name 128 characters

    if ".elasticbeanstalk.com" in takeover_domain:
        resource_type = "Elastic Beanstalk environment"
        parameters = [
            {"ParameterKey": "DomainName", "ParameterValue": takeover_domain.rsplit(".", 3)[0]},
            {"ParameterKey": "BucketName", "ParameterValue": f"{project}-{sanitised_domain}-content-{suffix}"[:63]},
            {"ParameterKey": "EnvironmentName", "ParameterValue": project},
        ]
        resource_name = stack_name

    else:
        resource_type = "S3 bucket"
        parameters = [{"ParameterKey": "DomainName", "ParameterValue": takeover_domain}]
        resource_name = takeover_domain

    print(f"creating CloudFormation stack {stack_name} in {region} region")

    try:

        with open(template, "r", encoding="utf-8") as f:
            template = f.read()

            cloudformation.create_stack(
                StackName=stack_name,
                TemplateBody=template,
                Parameters=parameters,
                NotificationARNs=[],
                Capabilities=["CAPABILITY_NAMED_IAM"],
                OnFailure="ROLLBACK",
                Tags=[
                    {"Key": "ResourceName", "Value": resource_name},
                    {"Key": "ResourceType", "Value": resource_type},
                    {"Key": "TakeoverAccount", "Value": get_account_name()},
                    {"Key": "VulnerableAccount", "Value": account},
                    {"Key": "VulnerableDomain", "Value": vulnerable_domain},
                ],
            )

            while time.time() < (time.time() + 900):  # 15mins to allow for ElasticBeanstalk creation time
                status = cloudformation.describe_stacks(StackName=stack_name)["Stacks"][0]["StackStatus"]
                if status == "CREATE_IN_PROGRESS":
                    print("resource creation in progress")
                    time.sleep(10)

                elif status == "CREATE_COMPLETE":
                    print("resource creation complete")

                    return True

                else:
                    print(f"resource creation failed with status {status}")

                    return False

            print("resource creation timed out")

            return False

    except exceptions.ClientError as e:
        print(e.response["Error"]["Code"])
        return False


def create_stack_eb_content(region, template, vulnerable_domain, account):

    session = boto3.Session(region_name=region)
    cloudformation = session.client("cloudformation")

    sanitised_domain = vulnerable_domain.replace(".", "-")
    if sanitised_domain.endswith("-"):
        sanitised_domain = sanitised_domain[:-1]

    stack_name = f"{project}-{sanitised_domain}-content"[:128]
    resource_type = "S3 bucket for Elastic Beanstalk content"
    bucket_name = f"{project}-{sanitised_domain}-content-{suffix}"[:63]
    parameters = [{"ParameterKey": "BucketName", "ParameterValue": bucket_name}]

    print(f"creating CloudFormation stack {stack_name} in {region} region")

    try:
        with open(template, "r", encoding="utf-8") as f:
            template = f.read()

            cloudformation.create_stack(
                StackName=stack_name,
                TemplateBody=template,
                Parameters=parameters,
                NotificationARNs=[],
                Capabilities=["CAPABILITY_NAMED_IAM"],
                OnFailure="ROLLBACK",
                Tags=[
                    {"Key": "ResourceName", "Value": bucket_name},
                    {"Key": "ResourceType", "Value": resource_type},
                    {"Key": "TakeoverAccount", "Value": get_account_name()},
                    {"Key": "VulnerableAccount", "Value": account},
                    {"Key": "VulnerableDomain", "Value": vulnerable_domain},
                ],
            )

            timeout = time.time() + 600  # 10 mins
            while time.time() < timeout:
                status = cloudformation.describe_stacks(StackName=stack_name)["Stacks"][0]["StackStatus"]
                if status == "CREATE_IN_PROGRESS":
                    print("resource creation in progress")
                    time.sleep(10)

                elif status == "CREATE_COMPLETE":
                    print("resource creation complete")
                    return bucket_name

                else:
                    print(f"resource creation failed with status {status}")

                    return None

            print("resource creation timed out")
            return None

    except exceptions.ClientError as e:
        print(e.response["Error"]["Code"])
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


def s3_upload_eb_content(path, bucket, region):

    session = boto3.Session(region_name=region)
    s3 = session.client("s3")

    print(f"uploading Elastic Beanstalk content to {bucket} S3 bucket in {region} region")

    for file in os.listdir(path):
        with open(os.path.join(path, file), "rb") as data:
            s3.upload_fileobj(data, bucket, file)


def s3_takeover(target, account, vulnerable_domain):

    if target.endswith("."):
        target = target[:-1]

    domain = target.rsplit(".", 4)[0]
    region = target.rsplit(".", 4)[2]

    print(f"Creating S3 bucket {domain} in {region} region")
    if create_stack(region, "s3.yaml", domain, vulnerable_domain, account):
        s3_upload("s3-content", domain, region)

        return True

    return False


def s3_delete_eb_content(bucket, region):

    session = boto3.Session(region_name=region)
    s3 = session.client("s3")

    print(f"deleting all content from {bucket} S3 bucket in {region} region")
    objects = {"Objects": [{"Key": "content.zip"}]}
    s3.delete_objects(Bucket=bucket, Delete=objects)


def delete_stack_eb_content(region, vulnerable_domain):

    session = boto3.Session(region_name=region)
    cloudformation = session.client("cloudformation")

    sanitised_domain = vulnerable_domain.replace(".", "-")
    if sanitised_domain.endswith("-"):
        sanitised_domain = sanitised_domain[:-1]

    stack_name = f"{project}-{sanitised_domain}-content"[:128]

    print(f"deleting CloudFormation stack {stack_name} in {region} region")

    cloudformation.delete_stack(StackName=stack_name)

    try:
        timeout = time.time() + 300  # 5 mins
        while time.time() < timeout:
            status = cloudformation.describe_stacks(StackName=stack_name)["Stacks"][0]["StackStatus"]
            if status == "DELETE_IN_PROGRESS":
                print("resource deletion in progress")
                time.sleep(10)

            elif status == "DELETE_COMPLETE":
                print("resource creation complete")

            else:
                print(f"resource creation failed with status {status}")

        print("resource creation timed out")

    except exceptions.ClientError as e:
        print(e.response["Error"]["Code"])


def eb_takeover(target, vulnerable_domain, account):

    if target.endswith("."):
        target = target[:-1]

    if vulnerable_domain.endswith("."):
        vulnerable_domain = vulnerable_domain[:-1]

    region = target.rsplit(".")[-3]
    print(f"Creating Elastic Beanstalk instance with domain name {target} in {region} region")
    bucket_name = create_stack_eb_content(region, "eb-content.yaml", vulnerable_domain, account)
    s3_upload_eb_content("eb-content", bucket_name, region)
    if create_stack(region, "eb-vpc.yaml", target, vulnerable_domain, account):
        if bucket_name is not None:
            s3_delete_eb_content(bucket_name, region)
            delete_stack_eb_content(region, vulnerable_domain)

        return True

    return False


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


def normalise_s3_takeover_domain(domain):

    if ".s3-website-" in domain:
        takeover_domain = (
            domain.split(".")[0] + ".s3-website." + domain.split(".")[1].split("-", 2)[2] + ".amazonaws.com"
        )

        return takeover_domain

    if ".s3." in domain:
        takeover_domain = domain.split(".")[0] + ".s3-website." + domain.split(".")[2] + ".amazonaws.com"

        return takeover_domain

    return domain


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
            if ".s3-website" in finding["Takeover"] or ".s3." in finding["Takeover"]:
                resource_type = "S3 Bucket"
                takeover_domain = normalise_s3_takeover_domain(finding["Takeover"])

                if s3_takeover(takeover_domain, finding["Account"], finding["Domain"]):

                    if takeover_successful(finding["Domain"]):
                        print(f"Takeover of {finding['Domain']} successful")
                        takeover_status = "success"

                    else:
                        print(f"Takeover of {finding['Domain']} unsuccessful")
                        takeover_status = "failure"

                else:
                    print(f"Takeover of {finding['Domain']} unsuccessful")
                    takeover_status = "failure"

                notification_json["Takeovers"].append(
                    {
                        "ResourceType": resource_type,
                        "TakeoverDomain": finding["Takeover"],
                        "TakeoverAccount": get_account_name(),
                        "VulnerableDomain": finding["Domain"],
                        "VulnerableAccount": finding["Account"],
                        "TakeoverStatus": takeover_status,
                    }
                )

                takeover_domains.append(finding["Domain"])

            elif ".elasticbeanstalk.com" in finding["Takeover"]:
                resource_type = "Elastic Beanstalk instance"

                if eb_takeover(finding["Takeover"], finding["Domain"], finding["Account"]):

                    if takeover_successful(finding["Domain"]):
                        print(f"Takeover of {finding['Domain']} successful")
                        takeover_status = "success"

                    else:
                        print(f"Takeover of {finding['Domain']} unsuccessful")
                        takeover_status = "failure"

                else:
                    print(f"Takeover of {finding['Domain']} unsuccessful")
                    takeover_status = "failure"

                notification_json["Takeovers"].append(
                    {
                        "ResourceType": resource_type,
                        "TakeoverDomain": finding["Takeover"],
                        "TakeoverAccount": get_account_name(),
                        "VulnerableDomain": finding["Domain"],
                        "VulnerableAccount": finding["Account"],
                        "TakeoverStatus": takeover_status,
                    }
                )

                takeover_domains.append(finding["Domain"])

            else:
                print("takeover domain type not supported")

        if len(takeover_domains) > 0:
            publish_to_sns(notification_json, "Hostile takeover prevention")

    except KeyError:
        pass
