from __future__ import print_function
import os, boto3, json, base64
import urllib.request, urllib.parse
import zlib

def lambda_handler(event, context):

    slack_url = os.environ['SLACK_WEBHOOK_URL']
    slack_channel = os.environ['SLACK_CHANNEL']
    slack_username = os.environ['SLACK_USERNAME']
    slack_emoji = os.environ['SLACK_EMOJI']

    subject = event['Records'][0]['Sns']['Subject']

    payload = {"channel": slack_channel, "username": slack_username, "icon_emoji": slack_emoji, "attachments": [],
               'text': subject}


    message = event['Records'][0]['Sns']['Message']
    json_data = json.loads(message)
    findings = json_data['Findings']

    fields = []

    slack_message = {
        "fallback": "A new message",
        "fields": [{"title": "Vulnerable domains"}]
    }

    for finding in findings:
        account = finding['Account']
        domain = finding['Domain']

        print(domain + " in " + account + " AWS Account" )

        slack_message['fields'].append({"value": domain + " in " + account + " AWS Account", "short": False} )

    payload['attachments'].append(slack_message)

    data = urllib.parse.urlencode({"payload": json.dumps(payload)}).encode("utf-8")
    req = urllib.request.Request(slack_url)
    urllib.request.urlopen(req, data)
