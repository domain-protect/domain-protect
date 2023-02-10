# domain-protect
![Release version](https://img.shields.io/badge/release-v0.4.0-blue.svg)
[![Python 3.x](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
![OWASP Manutiry](https://img.shields.io/badge/owasp-incubator%20project-53AAE5.svg)

* scan Amazon Route53 across an AWS Organization for domain records vulnerable to takeover
* scan [Cloudflare](docs/cloudflare.md) for vulnerable DNS records
* take over vulnerable subdomains yourself before attackers and bug bounty researchers
* automatically create known issues in [Bugcrowd](docs/bugcrowd.md) or [HackerOne](docs/hackerone.md)
* vulnerable domains in Google Cloud DNS can be detected by [Domain Protect for GCP](https://github.com/ovotech/domain-protect-gcp)

### blog posts
* [How we prevented subdomain takeovers and saved $000s](https://tech.ovoenergy.com/how-we-prevented-subdomain-takeovers-and-saved-000s/)
* [OVO vs. Bug Bounty researchers - round 2](https://tech.ovoenergy.com/ovo-vs-bug-bounty-researchers-round-2/)

### conference and meetup talks
* [OWASP London Chapter 2022](https://youtu.be/nw6uR0glJKk)
* [SANSCloudSecNext 2022](https://youtu.be/Boy8DYrC-Xw)
* [CloudSecurityLondon 2022](https://youtu.be/4Hg9bEvxTRo)

### deploy to security audit account

![Alt text](docs/images/domain-protect.png?raw=true "Domain Protect architecture")

### scan your entire AWS Organization

![Alt text](docs/images/multi-account.png?raw=true "Multi account setup")

### take over vulnerable domains in security account

<kbd>
  <img src="docs/images/takeover.png" width="500">
</kbd>

### receive alerts by Slack or email

<kbd>
  <img src="docs/images/new.png" width="600">
</kbd>

<kbd>
  <img src="docs/images/slack-ns.png" width="500">
</kbd>

<kbd>
  <img src="docs/images/fixed.png" width="400">
</kbd>

### deploy in your AWS Organization using GitHub Actions

![Alt text](docs/images/pipeline.png?raw=true "GitHub Actions pipeline")

### or manually scan from your laptop

![Alt text](docs/images/vulnerable-eb-cnames.png?raw=true "Detect vulnerable ElasticBeanstalk CNAMEs")

## documentation
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

## limitations
* this tool cannot guarantee 100% protection against subdomain takeover
* it currently only scans Amazon Route53 and Cloudflare, and only checks a limited number of takeover types
* vulnerable domains in Google Cloud DNS can be detected by [Domain Protect for GCP](https://github.com/ovotech/domain-protect-gcp)
