#!/usr/bin/env python
import os
import json
import boto3
import decimal

from utils.utils_aws import list_accounts

state_machine_arn = os.environ["STATE_MACHINE_ARN"]

def lambda_handler(event, context):  # pylint:disable=unused-argument

    accounts = list_accounts()
    print(accounts)

    input = []

    keys_to_remove = ["Arn", "Email", "Status", "JoinedMethod", "JoinedTimestamp"]

    for account in accounts:
        for key in keys_to_remove:
            del account[key]
        input.append(account)

    print(input)

    sm = boto3.client('stepfunctions')
    sm.start_execution(stateMachineArn=state_machine_arn, input=json.dumps(input))
