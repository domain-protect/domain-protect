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


def db_count_items(table_name):
    # counts number of items in DynamoDB table

    client = boto3.client("dynamodb")

    print(f"counting items in DynamoDB table {table_name}")

    return client.describe_table(TableName=table_name)["Table"]["ItemCount"]


def db_get_ip(ip):
    # gets IP address details from database

    client = boto3.client("dynamodb")

    print(f"querying DynamoDB table {db_get_ip_table_name()} for {ip}")

    response = client.get_item(
        TableName=db_get_ip_table_name(),
        Key={"IP": {"S": ip}},
    )

    try:
        item = response["Item"]

        return item

    except KeyError:

        return {}


def db_ip(ip, account, region, resource_type, cloud="AWS"):
    # checks to see if IP address already exists in the database
    # if so, updates the LastFoundTime
    # otherwise, adds IP address to database

    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client = boto3.client("dynamodb")
    table_name = db_get_ip_table_name()

    if not db_get_ip(ip):
        print(f"creating item {ip} in DynamoDB table {table_name}")

        client.put_item(
            TableName=table_name,
            Item={
                "IP": {"S": ip},
                "FoundDateTime": {"S": date_time},
                "LastDateTime": {"S": date_time},
                "Account": {"S": account},
                "Region": {"S": region},
                "ResourceType": {"S": resource_type},
                "Cloud": {"S": cloud},
            },
        )

    else:
        print(f"updating item {ip} in DynamoDB table {table_name}")

        client.update_item(
            TableName=table_name,
            Key={
                "IP": {"S": ip},
            },
            UpdateExpression="set LastDateTime=:t",
            ExpressionAttributeValues={":t": {"S": date_time}},
        )


def db_check_ip(ip, max_age_hours):
    # checks database for IP address
    # ignores if LastDateTime is older than specified number of hours
    # doesn't check age of manually entered exceptions

    date_time = datetime.datetime.now()
    item = db_get_ip(ip)

    if item:

        if "IP OK" in item["Account"]["S"]:

            return True

        last_date_time_string = item["LastDateTime"]["S"]
        last_date_time = datetime.datetime.strptime(last_date_time_string, "%Y-%m-%d %H:%M:%S")

        age = date_time - last_date_time

        if int(age.total_seconds()) < 3600 * max_age_hours:

            return True

    return False
