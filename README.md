# OWASP Domain Protect
![Release version](https://img.shields.io/badge/release-v0.4.2-blue.svg)
[![Python 3.x](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
![OWASP Maturity](https://img.shields.io/badge/owasp-incubator%20project-53AAE5.svg)

## Prevent subdomain takeover ...
![Alt text](docs/images/slack-webhook-notifications.png?raw=true "Domain Protect architecture")

## ... with serverless cloud infrastructure
![Alt text](docs/images/domain-protect.png?raw=true "Domain Protect architecture")

## OWASP Global AppSec Dublin - talk and demo
[![Global AppSec Dublin 2023](docs/images/global-appsec-dublin.png)](https://youtu.be/fLrRLmKZTvE)

## Features
* scan Amazon Route53 across an AWS Organization for domain records vulnerable to takeover
* scan [Cloudflare](docs/cloudflare.md) for vulnerable DNS records
* take over vulnerable subdomains yourself before attackers and bug bounty researchers
* automatically create known issues in [Bugcrowd](docs/bugcrowd.md) or [HackerOne](docs/hackerone.md)
* vulnerable domains in Google Cloud DNS can be detected by [Domain Protect for GCP](https://github.com/ovotech/domain-protect-gcp)
* [manual scans](manual_scans/aws/README.md) of cloud accounts with no installation

## Installation
* the simplest way to install is to use the separate [Domain Protect Deploy](https://github.com/domain-protect/domain-protect-deploy) repository with GitHub Actions deployment workflow
* for other methods see [Installation](docs/installation.md)

## Collaboration
We welcome collaborators! Please see the [OWASP Domain Protect website](https://owasp.org/www-project-domain-protect/) for more details.

## Documentation
[Manual scans - AWS](manual_scans/aws/README.md)<br>
[Manual scans - CloudFlare](manual_scans/cloudflare/README.md)<br>
[Architecture](docs/architecture.md)<br>
[Database](docs/database.md)<br>
[Reports](docs/reports.md)<br>
[Automated takeover](docs/automated-takeover.md) *optional feature*<br>
[Cloudflare](docs/cloudflare.md) *optional feature*<br>
[Bugcrowd](docs/bugcrowd.md) *optional feature*<br>
[HackerOne](docs/hackerone.md) *optional feature*<br>
[Vulnerability types](docs/vulnerability-types.md)<br>
[Vulnerable A records (IP addresses)](docs/a-records.md) *optional feature*<br>
[Requirements](docs/requirements.md)<br>
[Installation](docs/installation.md)<br>
[Slack Webhooks](docs/slack-webhook.md)<br>
[AWS IAM policies](docs/aws-iam-policies.md)<br>
[CI/CD](docs/ci-cd.md)<br>
[Development](docs/development.md)<br>
[Code Standards](docs/code-standards.md)<br>
[Automated Tests](docs/automated-tests.md)<br>
[Manual Tests](docs/manual-tests.md)<br>
[Conference Talks and Blog Posts](docs/talks.md)<br>

## Limitations
This tool cannot guarantee 100% protection against subdomain takeovers.
