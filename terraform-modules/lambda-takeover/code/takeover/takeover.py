import json
import os
import boto3

project = os.environ["PROJECT"]

def create_stack(region, template, takeover_domain, vulnerable_domain, account):

    session = boto3.Session(region_name=region)
    cloudformation = session.client("cloudformation")

    sanitised_domain = vulnerable_domain.replace(".", "-")

    stack_name = f"{project}-{sanitised_domain}"

    print(f"creating CloudFormation stack {vulnerable_domain} in {region} region")

    with open(template, "r") as f:
        template = f.read() 

        cloudformation.create_stack(
            StackName=stack_name,
            TemplateBody=template,
            Parameters=[
                {
                    'ParameterKey': 'DomainTag',
                    'ParameterValue': f"{project}-vulnerable-domain"
                },
                {
                    'ParameterKey': 'DomainName',
                    'ParameterValue': takeover_domain
                },
                {
                    'ParameterKey': 'AccountTag',
                    'ParameterValue': f"{project}-account"
                },
                {
                    'ParameterKey': 'AccountName',
                    'ParameterValue': account
                }
            ],
            NotificationARNs=[],
            Capabilities=["CAPABILITY_NAMED_IAM"],
            OnFailure="ROLLBACK",
            Tags=[
                {"Key": f"{project}-vulnerable-domain", "Value": vulnerable_domain},
                {"Key": f"{project}-account", "Value": account},
            ],
        )

        return None


def s3_upload(path, bucket, region):

    session = boto3.Session(region_name=region)
    s3 = session.client("s3")

    print(f"uploading content to {bucket} S3 bucket in {region} region")

    for file in os.listdir(path):
            s3.upload_file(os.path.join(path, file), bucket, file, ExtraArgs={'ACL': 'public-read', 'ContentType': 'text/html'})


def s3_takeover(target, account):

    domain = target.rsplit(".", 4)[0]
    region = target.rsplit(".", 4)[2]

    print(f"Creating S3 bucket {domain} in {region} region")

    create_stack(region, "s3.yaml", domain, domain, account)
    s3_upload("content", domain, region)


def lambda_handler(event, context):  # pylint:disable=unused-argument

    message = event["Records"][0]["Sns"]["Message"]
    json_data = json.loads(message)
    findings = json_data["Findings"]

    for finding in findings:
        print(
            f"Attempting takeover of {finding['Takeover']} for vulnerable domain {finding['Domain']} in {finding['Account']} AWS Account"
        )
        if ".s3-website." in finding['Takeover']:
            s3_takeover(finding['Takeover'], finding['Account'])
