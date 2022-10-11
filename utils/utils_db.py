import datetime
import os

import boto3

from utils.utils_dates import calc_prev_month_start

project = os.environ["PROJECT"]
env_name = os.environ["TERRAFORM_WORKSPACE"]
base_table_name = "VulnerableDomains"


def db_get_table_name():
    # constructs the DynamoDB table name, e.g. DomainProtectVulnerableDomainsDev

    capitalised_project = project.replace("-", " ").title().replace(" ", "")
    capitalised_env_name = env_name.title()
    table_name = f"{capitalised_project}{base_table_name}{capitalised_env_name}"

    return table_name


def db_list_vulnerabilities(domain):
    # returns list of vulnerabilities, fixed or unfixed, for a specified domain
    # ExpressionAttributeNames is used because Domain is a reserved word in DynamoDB

    client = boto3.client("dynamodb")

    print(f"querying DynamoDB table {db_get_table_name()} for {domain}")

    response = client.query(
        TableName=db_get_table_name(),
        KeyConditionExpression="#D = :partitionkeyval",
        ExpressionAttributeNames={"#D": "Domain"},
        ExpressionAttributeValues={":partitionkeyval": {"S": domain}},
    )

    return response["Items"]


def db_get_unfixed_vulnerability_found_date_time(domain):
    # gets the unfixed vulnerability for a specified domain

    vulnerabilities = db_list_vulnerabilities(domain)

    for vulnerability in vulnerabilities:
        try:
            vulnerability["FixedDateTime"]

        except KeyError:
            return vulnerability["FoundDateTime"]

    return {}


def db_vulnerability_found(domain, account, vulnerability_type, resource_type, cloud="AWS"):
    # creates a new item in DynamoDB when Domain Protect finds a vulnerability
    # checks first to see if the unfixed vulnerability already exists

    client = boto3.client("dynamodb")

    if db_get_unfixed_vulnerability_found_date_time(domain):
        print(f"{domain} unfixed vulnerability already exists")

    else:
        print(f"creating item {domain} in DynamoDB table {db_get_table_name()}")

        found_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        client.put_item(
            TableName=db_get_table_name(),
            Item={
                "Domain": {"S": domain},
                "FoundDateTime": {"S": found_date_time},
                "Account": {"S": account},
                "VulnerabilityType": {"S": vulnerability_type},
                "Cloud": {"S": cloud},
                "ResourceType": {"S": resource_type},
            },
        )


def db_vulnerability_fixed(domain):
    # updates an existing item in DynamoDB when Domain Protect identifies that a domain is no longer vulnerable

    try:
        found_date_time = db_get_unfixed_vulnerability_found_date_time(domain)["S"]
        client = boto3.client("dynamodb")

        print(f"updating {domain} created {found_date_time} with FixedDateTime")

        fixed_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            client.update_item(
                TableName=db_get_table_name(),
                Key={
                    "Domain": {"S": domain},
                    "FoundDateTime": {"S": found_date_time},
                },
                UpdateExpression="set FixedDateTime=:t",
                ExpressionAttributeValues={":t": {"S": fixed_date_time}},
                ConditionExpression="attribute_not_exists(FixedDateTime)",
            )

        except client.exceptions.ConditionalCheckFailedException:
            print(f"ERROR: vulnerable domain {domain} created {found_date_time} already fixed")

    except KeyError:
        print(f"{domain} vulnerability not found or already fixed")


def db_list_all_unfixed_vulnerabilities():
    # returns list of all unfixed vulnerabilities

    client = boto3.client("dynamodb")

    print(f"querying DynamoDB table {db_get_table_name()} for unfixed vulnerabilities")

    response = client.scan(
        TableName=db_get_table_name(),
        ProjectionExpression="#D, VulnerabilityType, Cloud, ResourceType, Account",
        FilterExpression="attribute_not_exists(FixedDateTime)",
        ExpressionAttributeNames={"#D": "Domain"},
    )

    return response["Items"]


def scan_table_page_item_count(start_date, client, exclusive_start_key=None):
    # returns the count of items for a single page in a query

    kwargs = {
        "TableName": db_get_table_name(),
        "Select": "COUNT",
        "FilterExpression": "#fd >= :startdate",
        "ExpressionAttributeNames": {"#fd": "FoundDateTime"},
        "ExpressionAttributeValues": {":startdate": {"S": start_date}},
    }
    if exclusive_start_key:
        kwargs["ExclusiveStartKey"] = exclusive_start_key

    return client.scan(**kwargs)


def paged_scan(client, run_func):
    # iterator function that returns each page of a run_func

    scan = run_func(client)
    yield scan

    while "LastEvaluatedKey" in scan:
        scan = run_func(client, scan["LastEvaluatedKey"])
        yield scan


def count_previous_month_page(client, exclusive_start_key=None):
    # returns a single page of the last months count

    prev_month_start = calc_prev_month_start(datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")

    return scan_table_page_item_count(prev_month_start, client, exclusive_start_key)


def count_previous_month():
    # returns the count of last months vulnerable domains

    client = boto3.client("dynamodb")
    count = sum(c["Count"] ** 2 for c in paged_scan(client, count_previous_month_page))
    return count


def count_previous_year_page(client, exclusive_start_key=None):
    # returns a single page of the last years count

    year_start = (
        datetime.datetime.now().replace(day=1, month=1, hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
    )
    return scan_table_page_item_count(year_start, client, exclusive_start_key)


def count_previous_year():
    # returns the count of the last years vulnerable domains

    client = boto3.client("dynamodb")
    count = sum([c["Count"] for c in paged_scan(client, count_previous_year_page)])
    return count
