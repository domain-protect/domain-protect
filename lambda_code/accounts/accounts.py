#!/usr/bin/env python
import json
import os

import boto3

from utils.utils_aws import list_accounts

state_machine_arn = os.environ["STATE_MACHINE_ARN"]


def lambda_handler(event, context):  # pylint:disable=unused-argument
    # lists all AWS accounts in organization and sends in JSON format to Step Functions state machine

    accounts = list_accounts()
    print(accounts)

    input_data = []

    for account in accounts:
        account_id = account["Id"]
        account_name = account["Name"]
        input_data.append({"Id": account_id, "Name": account_name})

    print(input_data)

    sm = boto3.client("stepfunctions")
    sm.start_execution(stateMachineArn=state_machine_arn, input=json.dumps(input_data))
