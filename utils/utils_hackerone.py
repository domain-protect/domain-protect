import os

import requests

from utils.utils_globalvars import requests_timeout

hackerone_api_token = os.environ.get("HACKERONE_API_TOKEN")
hackerone_base_url = "https://api.hackerone.com/v1"
project = os.environ.get("PROJECT")


def hackerone_api_headers():

    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    return headers


def hackerone_get_program_handle():

    response = requests.get(
        url=f"{hackerone_base_url}/me/programs",
        headers=hackerone_api_headers(),
        auth=(project, hackerone_api_token),
        timeout=requests_timeout(),
    )

    data = response.json()["data"]
    program_handle = data[0]["attributes"]["handle"]
    print(f"HackerOne program handle: {program_handle}")

    return program_handle


def hackerone_create_report(domain, resource_type, vulnerability_type):

    program_handle = hackerone_get_program_handle()
    title = f"Subdomain {domain} vulnerable to takeover"
    vulnerability_information = (
        f"Subdomain [{domain}](http://{domain}) is vulnerable to domain takeover with **{vulnerability_type}** \n"
        f"vulnerability type and **{resource_type}** resource \n\n"
        f"Created as a known issue by {program_handle} administrators"
    )

    attributes = {
        "team_handle": program_handle,
        "title": title,
        "vulnerability_information": vulnerability_information,
        "impact": "Reputational damage, credential harvesting, malware distribution",
        "severity_rating": "high",
        "weakness_id": "75",
        "source": project,
    }

    data = {
        "data": {
            "type": "report",
            "attributes": attributes,
        },
    }

    response = requests.post(
        url=f"{hackerone_base_url}/reports",
        headers=hackerone_api_headers(),
        auth=(project, hackerone_api_token),
        json=data,
        timeout=requests_timeout(),
    )

    if response.status_code == 201:

        submission_id = response.json()["data"]["id"]
        print(f"HackerOne submission {submission_id} created for {domain} vulnerable to takeover")

        return submission_id

    print(f"HackerOne submission creation failed for {domain}")
    print(f"response status {response.status_code}")
    print(f"reason: {response.reason}")

    return ""
