# domain-protect

## Table of Contents

- [domain-protect](#domain-protect)
  - [Table of Contents](#table-of-contents)
  - [Purpose](#purpose)
  - [Blog posts](#blog-posts)
  - [Conference and meetup talks](#conference-and-meetup-talks)
  - [Resources deployed in security audit account](#resources-deployed-in-security-audit-account)
  - [How it works](#how-it-works)
  - [Functionality](#functionality)
  - [Deployment/Installation](#deploymentinstallation)
  - [More Documentation](#more-documentation)
  - [Limitations](#limitations)


## Purpose

- scan Amazon Route53 across an AWS Organization for domain records vulnerable to takeover
- scan [Cloudflare](docs/cloudflare.md) for vulnerable DNS records
- take over vulnerable subdomains yourself before attackers and bug bounty researchers
- automatically create known issues in [Bugcrowd](docs/bugcrowd.md) or [HackerOne](docs/hackerone.md)
- vulnerable domains in Google Cloud DNS can be detected by [Domain Protect for GCP](https://github.com/ovotech/domain-protect-gcp)

## Blog posts

- [How we prevented subdomain takeovers and saved $000s](https://tech.ovoenergy.com/how-we-prevented-subdomain-takeovers-and-saved-000s/)
- [OVO vs. Bug Bounty researchers - round 2](https://tech.ovoenergy.com/ovo-vs-bug-bounty-researchers-round-2/)

## Conference and meetup talks

- [OWASP London Chapter 2022](https://youtu.be/nw6uR0glJKk)
- [SANSCloudSecNext 2022](https://youtu.be/Boy8DYrC-Xw)
- [CloudSecurityLondon 2022](https://youtu.be/4Hg9bEvxTRo)

## Resources deployed in security audit account

![Alt text](docs/images/domain-protect.png?raw=true "Domain Protect architecture")

## How it works

![Alt text](docs/images/multi-account.png?raw=true "Multi account setup")

- (1)(2) A lambda function in security audit account is triggered by cloudwatch event to assume to a role in the management account and get all the accounts in the organization.
- (3) The list of all accounts are then passed to step function as parameters
- (4)(5)(6) Step function then triggers lambda functions to scan route53 and all resources like EC2 in all accounts
- (7) All violations are stored in DynamoDB in security audit account
- (8) As one of the steps in step function, a lambda function will be invoked to retrieve findings from DynamoDB to publish to SNS topic
- (9)(10) Once message comes in SNS topic, it will trigger another lambda to notify users via slack or email

## Functionality

- Identifying vulnerable domains in all accounts
- Taking over vulnerable domains and create resources to prevent subdomain takeover in security account. More [here](https://tech.ovoenergy.com/ovo-vs-bug-bounty-researchers-round-2/)

<kbd>
  <img src="docs/images/takeover.png" width="500">
</kbd>

- Receiving alerts by Slack or email

<kbd>
  <img src="docs/images/new.png" width="600">
</kbd>

<kbd>
  <img src="docs/images/slack-ns.png" width="500">
</kbd>

<kbd>
  <img src="docs/images/fixed.png" width="400">
</kbd>

## Deployment/Installation

Please check out our [Requirements](docs/requirements.md) first. We offer three examples to run this tool

1. Github Actions

You can deploy resources in this repo using GitHub Actions. Follow detailed instructions in separate [Domain Protect Deploy](https://github.com/domain-protect/domain-protect-deploy)

![Alt text](docs/images/pipeline.png?raw=true "GitHub Actions pipeline")

2. Atlantis

Some organizations are using [atlantis](https://www.runatlantis.io/) as a way to manage infrastructure. Atlantis behind the scene runs terraform. Please refer [Installation](docs/installation.md) for more details on the changes you need to do to make this work.

3. Manual run in local environment
![Alt text](docs/images/vulnerable-eb-cnames.png?raw=true "Detect vulnerable ElasticBeanstalk CNAMEs")
More instructions on this are in [Installation](docs/installation.md).

## More Documentation

1. [Manual scans - AWS](manual_scans/aws/README.md)
2. [Manual scans - CloudFlare](manual_scans/cloudflare/README.md)
3. [Architecture](docs/architecture.md)
4. [Database](docs/database.md)
5. [Reports](docs/reports.md)
6. [Automated takeover](docs/automated-takeover.md) *optional feature*
7. [Cloudflare](docs/cloudflare.md) *optional feature*
8. [Bugcrowd](docs/bugcrowd.md) *optional feature*
9. [HackerOne](docs/hackerone.md) *optional feature*
10. [Vulnerability types](docs/vulnerability-types.md)
11. [Vulnerable A records (IP addresses)](docs/a-records.md) *optional feature*
12. [Requirements](docs/requirements.md)
13. [Installation](docs/installation.md)
14. [AWS IAM policies](docs/aws-iam-policies.md)
15. [CI/CD](docs/ci-cd.md)
16. [Development](docs/development.md)
17. [Code Standards](docs/code-standards.md)
18. [Automated Tests](docs/automated-tests.md)
19. [Manual Tests](docs/manual-tests.md)

## Limitations

- this tool cannot guarantee 100% protection against subdomain takeover
- it currently only scans Amazon Route53 and Cloudflare, and only checks a limited number of takeover types
- vulnerable domains in Google Cloud DNS can be detected by [Domain Protect for GCP](https://github.com/ovotech/domain-protect-gcp)
