from __future__ import print_function
import json
import os
import requests
from utils.utils_dates import last_month_start

from utils.utils_db import count_previous_month, count_previous_year, db_get_table_name
from utils.utils_db_ips import db_count_items


def build_markdown_block(text):
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def build_message():
    last_month = count_previous_month()
    last_year = count_previous_year()
    total = db_count_items(db_get_table_name())

    last_month = last_month_start()
    last_month_year_text = last_month.strftime("%B %Y")
    last_year_text = last_month.strftime("%Y")

    blocks = [
        build_markdown_block(f"Total new findings for {last_month_year_text}: *{last_month}*"),
        build_markdown_block(f"Total new findings for {last_year_text}: *{last_year}*"),
        build_markdown_block(f"Total findings all time: *{total}*"),
    ]
    return {"blocks": blocks}


def lambda_handler(event, context):  # pylint:disable=unused-argument

    slack_url = os.environ["SLACK_WEBHOOK_URL"]
    slack_channel = os.environ["SLACK_CHANNEL"]
    slack_username = os.environ["SLACK_USERNAME"]
    slack_emoji = os.environ["SLACK_EMOJI"]
    subject = "Domain Protect Monthly Stats"

    payload = {
        "channel": slack_channel,
        "username": slack_username,
        "icon_emoji": slack_emoji,
        "attachments": [build_message()],
        "text": subject,
    }

    response = requests.post(
        slack_url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )

    if response.status_code != 200:
        ValueError(f"Request to Slack returned error {response.status_code}:\n{response.text}")

    else:
        print(f"Stats message sent to {slack_channel} Slack channel")
