import datetime
import json
import os

import requests

from utils.utils_dates import calc_prev_month_start
from utils.utils_globalvars import requests_timeout


slack_url = os.environ["SLACK_WEBHOOK_URL"]
slack_channel = os.environ["SLACK_CHANNEL"]
slack_webhook_type = os.environ["SLACK_WEBHOOK_TYPE"]
slack_username = os.environ["SLACK_USERNAME"]
slack_emoji = os.environ["SLACK_EMOJI"]
slack_fix_emoji = os.environ["SLACK_FIX_EMOJI"]
slack_new_emoji = os.environ["SLACK_NEW_EMOJI"]


def findings_message(json_data):

    try:
        findings = json_data["Findings"]

        slack_message = {"fallback": "A new message", "fields": [{"title": "Vulnerable domains"}]}

        for finding in findings:

            if finding["Account"] == "Cloudflare":
                message = f"{finding['Domain']} in Cloudflare"

            else:
                message = f"{finding['Domain']} in {finding['Account']} AWS Account"

            print(message)
            slack_message["fields"].append({"value": message, "short": False})

        return slack_message

    except KeyError:

        return None


def takeovers_message(json_data):

    try:
        takeovers = json_data["Takeovers"]

        slack_message = {"fallback": "A new message", "fields": [{"title": "Domain takeover status"}]}

        for takeover in takeovers:

            success_message = (
                f"{takeover['ResourceType']} {takeover['TakeoverDomain']} "
                f"successfully created in {takeover['TakeoverAccount']} AWS account "
                f"to protect {takeover['VulnerableDomain']} domain in {takeover['VulnerableAccount']} account"
            )

            failure_message = (
                f"{takeover['ResourceType']} {takeover['TakeoverDomain']} creation "
                f"failed in {takeover['TakeoverAccount']} AWS account to protect {takeover['VulnerableDomain']} "
                f"domain in {takeover['VulnerableAccount']} account"
            )

            if takeover["TakeoverStatus"] == "success":
                print(success_message)
                slack_message["fields"].append(
                    {
                        "value": success_message,
                        "short": False,
                    },
                )

            if takeover["TakeoverStatus"] == "failure":
                print(failure_message)
                slack_message["fields"].append(
                    {
                        "value": failure_message,
                        "short": False,
                    },
                )

        return slack_message

    except KeyError:

        return None


def resources_message(json_data):

    try:
        stacks = json_data["Resources"]

        slack_message = {"fallback": "A new message", "fields": [{"title": "Resources preventing hostile takeover"}]}
        resource_name = resource_type = takeover_account = vulnerable_account = vulnerable_domain = ""

        for tags in stacks:

            for tag in tags:

                if tag["Key"] == "ResourceName":
                    resource_name = tag["Value"]

                elif tag["Key"] == "ResourceType":
                    resource_type = tag["Value"]

                elif tag["Key"] == "TakeoverAccount":
                    takeover_account = tag["Value"]

                elif tag["Key"] == "VulnerableAccount":
                    vulnerable_account = tag["Value"]

                elif tag["Key"] == "VulnerableDomain":
                    vulnerable_domain = tag["Value"]

            message = (
                f"{resource_type} {resource_name} in {takeover_account} AWS account protecting "
                f"{vulnerable_domain} domain in {vulnerable_account} Account"
            )

            print(message)

            slack_message["fields"].append(
                {
                    "value": message,
                    "short": False,
                },
            )

        slack_message["fields"].append(
            {
                "value": "After fixing DNS issues, delete resources and CloudFormation stacks",
                "short": False,
            },
        )

        return slack_message

    except KeyError:

        return None


def fixed_message(json_data):

    try:
        fixes = json_data["Fixed"]

        slack_message = {"fallback": "A new message", "fields": [{"title": "Vulnerable domains fixed or taken over"}]}

        for fix in fixes:

            if fix["Account"] == "Cloudflare":
                message = f"{fix['Domain']} in Cloudflare"

            else:
                message = f"{fix['Domain']} in {fix['Account']} AWS Account"

            print(message)
            slack_message["fields"].append(
                {
                    "value": message,
                    "short": False,
                },
            )

        return slack_message

    except KeyError:

        return None


def current_message(json_data):

    try:
        vulnerabilities = json_data["Current"]

        slack_message = {
            "fallback": "A new message",
            "fields": [{"title": "Vulnerable domains fixed or taken over"}],
        }

        for vulnerability in vulnerabilities:

            if vulnerability["Account"] == "Cloudflare":
                message = (
                    f"{vulnerability['Domain']} {vulnerability['VulnerabilityType']} "
                    f"record in Cloudflare DNS with {vulnerability['ResourceType']} resource"
                )

            else:
                message = (
                    f"{vulnerability['Domain']} {vulnerability['VulnerabilityType']} record in "
                    f"{vulnerability['Account']} AWS Account with {vulnerability['ResourceType']} resource"
                )

            print(message)
            slack_message["fields"].append(
                {
                    "value": message,
                    "short": False,
                },
            )

        return slack_message

    except KeyError:

        return None


def new_message(json_data):

    try:
        vulnerabilities = json_data["New"]

        slack_message = {
            "fallback": "A new message",
            "fields": [{"title": "New vulnerable domains"}],
        }

        for vulnerability in vulnerabilities:

            try:
                if vulnerability["Bugcrowd"] and vulnerability["Bugcrowd"] != "N/A":
                    bugbounty_notification = ":bugcrowd: Bugcrowd issue created"

                elif not vulnerability["Bugcrowd"]:
                    bugbounty_notification = ":bugcrowd: Bugcrowd issue creation failed"

                elif vulnerability["HackerOne"] and vulnerability["HackerOne"] != "N/A":
                    bugbounty_notification = ":hackerone: HackerOne issue created"

                elif not vulnerability["HackerOne"]:
                    bugbounty_notification = ":hackerone: HackerOne issue creation failed"

                if vulnerability["Account"] == "Cloudflare":
                    message = (
                        f"{vulnerability['Domain']} {vulnerability['VulnerabilityType']} "
                        f"record in Cloudflare DNS with {vulnerability['ResourceType']} resource "
                        f"{bugbounty_notification}"
                    )

                else:
                    message = (
                        f"{vulnerability['Domain']} {vulnerability['VulnerabilityType']} record in "
                        f"{vulnerability['Account']} AWS Account with {vulnerability['ResourceType']} resource "
                        f"{bugbounty_notification}"
                    )

            except KeyError:
                if vulnerability["Account"] == "Cloudflare":
                    message = (
                        f"{vulnerability['Domain']} {vulnerability['VulnerabilityType']} "
                        f"record in Cloudflare DNS with {vulnerability['ResourceType']} resource"
                    )

                else:
                    message = (
                        f"{vulnerability['Domain']} {vulnerability['VulnerabilityType']} record in "
                        f"{vulnerability['Account']} AWS Account with {vulnerability['ResourceType']} resource"
                    )

            print(message)
            slack_message["fields"].append(
                {
                    "value": message,
                    "short": False,
                },
            )

        return slack_message

    except KeyError:

        return None


def build_markdown_block(text):
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def monthly_stats_message(json_data):
    last_month = calc_prev_month_start(datetime.datetime.now())
    last_month_year_text = last_month.strftime("%B %Y")
    last_year_text = last_month.strftime("%Y")

    try:
        blocks = [
            build_markdown_block(f"Total new findings for {last_month_year_text}: *{json_data['LastMonth']}*"),
            build_markdown_block(f"Total new findings for {last_year_text}: *{json_data['LastYear']}*"),
            build_markdown_block(f"Total findings all time: *{json_data['Total']}*"),
        ]
        return {"blocks": blocks}
    except KeyError:
        return None


def lambda_handler(event, context):  # pylint:disable=unused-argument

    slack_message = {}
    subject = event["Records"][0]["Sns"]["Subject"]

    payload = {
        "channel": slack_channel,
        "username": slack_username,
        "icon_emoji": slack_emoji,
        "attachments": [],
        "text": subject,
    }

    message = event["Records"][0]["Sns"]["Message"]
    json_data = json.loads(message)

    if findings_message(json_data) is not None:
        slack_message = findings_message(json_data)

    elif takeovers_message(json_data) is not None:
        slack_message = takeovers_message(json_data)

    elif resources_message(json_data) is not None:
        slack_message = resources_message(json_data)

    elif current_message(json_data) is not None and slack_webhook_type == "app":
        slack_message = current_message(json_data)
        payload["text"] = f"{slack_emoji} {subject}"

    elif current_message(json_data) is not None:
        slack_message = current_message(json_data)

    elif new_message(json_data) is not None and slack_webhook_type == "app":
        slack_message = new_message(json_data)
        payload["text"] = f"{slack_new_emoji} {subject}"

    elif new_message(json_data) is not None:
        slack_message = new_message(json_data)
        payload["icon_emoji"] = slack_new_emoji

    elif fixed_message(json_data) is not None and slack_webhook_type == "app":
        slack_message = fixed_message(json_data)
        payload["text"] = f"{slack_fix_emoji} {subject}"

    elif fixed_message(json_data) is not None:
        slack_message = fixed_message(json_data)
        payload["icon_emoji"] = slack_fix_emoji

    elif monthly_stats_message(json_data) is not None:
        slack_message = monthly_stats_message(json_data)
        payload["icon_emoji"] = slack_fix_emoji

    if len(slack_message) > 0:
        payload["attachments"].append(slack_message)

    response = requests.post(
        slack_url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=requests_timeout(),
    )

    if response.status_code != 200:
        ValueError(f"Request to Slack returned error {response.status_code}:\n{response.text}")

    else:
        print(f"Message sent to {slack_channel} Slack channel")
