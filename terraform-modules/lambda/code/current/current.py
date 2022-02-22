#!/usr/bin/env python
import json

from utils.utils_aws import publish_to_sns
from utils.utils_db import db_list_all_unfixed_vulnerabilities


def lambda_handler(event, context):  # pylint:disable=unused-argument
    # gets a list of current vulnerabilities from DynamoDB and sends to SNS

    vulnerabilities = db_list_all_unfixed_vulnerabilities()
    json_data = {"Current": []}

    for vulnerability in vulnerabilities:
        domain = vulnerability["Domain"]["S"]
        vulnerability_type = vulnerability["VulnerabilityType"]["S"]
        resource_type = vulnerability["ResourceType"]["S"]
        cloud = vulnerability["Cloud"]["S"]
        account = vulnerability["Account"]["S"]

        json_data["Current"].append(
            {
                "Domain": domain,
                "VulnerabilityType": vulnerability_type,
                "ResourceType": resource_type,
                "Cloud": cloud,
                "Account": account,
            }
        )

    if len(vulnerabilities) == 0:
        print("No current vulnerabilities")

    else:
        print(json.dumps(json_data, sort_keys=True, indent=2))
        publish_to_sns(json_data, "Vulnerable domains")
