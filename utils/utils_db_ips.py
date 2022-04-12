import datetime
import os

import boto3

project = os.environ["PROJECT"]
env_name = os.environ["TERRAFORM_WORKSPACE"]
ip_base_table_name = "IPs"


def db_get_ip_table_name():
    # constructs the DynamoDB IP table name, e.g. DomainProtectIPsDev

    capitalised_project = project.replace("-", " ").title().replace(" ", "")
    capitalised_env_name = env_name.title()
    table_name = f"{capitalised_project}{ip_base_table_name}{capitalised_env_name}"

    return table_name


def db_get_ip(ip):
    # returns list of vulnerabilities, fixed or unfixed, for a specified domain
    # ExpressionAttributeNames is used because Domain is a reserved word in DynamoDB

    client = boto3.client("dynamodb")

    print(f"querying DynamoDB table {db_get_ip_table_name()} for {ip}")

    response = client.query(
        TableName=db_get_ip_table_name(),
        KeyConditionExpression="#D = :partitionkeyval",
        ExpressionAttributeNames={"#D": "IP"},
        ExpressionAttributeValues={":partitionkeyval": {"S": ip}},
    )

    return response["Items"]


def db_ip(ip, account, region, resource_type, cloud="AWS"):
    # creates a new item in DynamoDB when Domain Protect finds an IP address
    # checks first to see if the IP address already exists

    client = boto3.client("dynamodb")

    if not db_get_ip(ip):
        print(f"creating item {ip} in DynamoDB table {db_get_ip_table_name()}")

        found_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        client.put_item(
            TableName=db_get_ip_table_name(),
            Item={
                "IP": {"S": ip},
                "FoundDateTime": {"S": found_date_time},
                "Account": {"S": account},
                "Region": {"S": region},
                "ResourceType": {"S": resource_type},
                "Cloud": {"S": cloud},
            },
        )
