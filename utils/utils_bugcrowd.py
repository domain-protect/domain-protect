import os
import requests

requests_timeout = os.environ["requests_timeout"]
bugcrowd_api_key = os.environ["BUGCROWD_API_KEY"]
bugcrowd_email = os.environ["BUGCROWD_EMAIL"]
bugcrowd_state = os.environ["BUGCROWD_STATE"]
bugcrowd_base_url = "https://api.bugcrowd.com"
project = os.environ["PROJECT"]


def bugcrowd_api_headers():

    token_string = f"Token {bugcrowd_api_key}"
    headers = {"Authorization": token_string, "Accept": "application/vnd.bugcrowd.v4+json"}
    return headers


def bugcrowd_get_org_id():

    response = requests.get(url=f"{bugcrowd_base_url}/programs", headers=bugcrowd_api_headers(), timeout=requests_timeout)

    data = response.json()["data"]
    org_id = data[0]["id"]
    print(f"BugCrowd Organization ID: {org_id}")

    return org_id


def bugcrowd_get_program_name():

    response = requests.get(url=f"{bugcrowd_base_url}/programs", headers=bugcrowd_api_headers(), timeout=requests_timeout)

    data = response.json()["data"]
    program_name = data[0]["attributes"]["name"]
    print(f"Bugcrowd Program Name: {program_name}")

    return program_name


def bugcrowd_create_submission(domain, resource_type, vulnerability_type):

    org_id = bugcrowd_get_org_id()
    title = f"Subdomain {domain} vulnerable to takeover"
    description = (
        f"Subdomain {domain} is vulnerable to domain takeover with {vulnerability_type} \n"
        f"vulnerability type and {resource_type} resource \n"
        f"Created as a known issue by {bugcrowd_get_program_name()} administrators"
    )

    attributes = {
        "title": title,
        "description": description,
        "severity": 3,
        "vrt_id": "server_security_misconfiguration.misconfigured_dns",
        "state": bugcrowd_state,
        "researcher_email": bugcrowd_email,
    }

    data = {
        "data": {
            "type": "submission",
            "attributes": attributes,
            "relationships": {"program": {"data": {"type": "program", "id": org_id}}},
        }
    }

    response = requests.post(
        url=f"{bugcrowd_base_url}/submissions", headers=bugcrowd_api_headers(), json=data, timeout=requests_timeout
    )

    if response.status_code == 201:

        submission_id = response.json()["data"]["id"]
        print(f"Bugcrowd submission {submission_id} created for {domain} vulnerable to takeover")

        return submission_id

    print(f"Bugcrowd submission creation failed for {domain}")
    print(f"response status {response.status_code}")
    print(f"reason: {response.reason}")

    return ""


def bugcrowd_create_comment(submission_id, domain):

    capitalised_project = project.replace("-", " ").title()

    comment_body = (
        f"Subdomain {domain} is vulnerable to domain takeover \n"
        f"Known issue created by {capitalised_project} for {bugcrowd_get_program_name()} administrators"
    )

    data = {
        "data": {
            "type": "comment",
            "attributes": {"body": comment_body, "visibility_scope": "everyone"},
            "relationships": {"submission": {"data": {"type": "submission", "id": submission_id}}},
        }
    }

    response = requests.post(url=f"{bugcrowd_base_url}/comments", headers=bugcrowd_api_headers(), json=data, timeout=requests_timeout)

    if response.status_code == 201:

        print(f"Comment added to Bugcrowd submission {submission_id}")

        return True

    print(f"Comment creation failed for Bugcrowd submission {submission_id}")
    print(f"response status {response.status_code}")
    print(f"reason: {response.reason}")

    return False


def bugcrowd_create_issue(domain, resource_type, vulnerability_type):

    submission_id = bugcrowd_create_submission(domain, resource_type, vulnerability_type)
    if bugcrowd_create_comment(submission_id, domain):

        return True

    return False
