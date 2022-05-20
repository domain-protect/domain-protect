# domain-protect
* scan Amazon Route53 across an AWS Organization for domain records vulnerable to takeover
* scan [Cloudflare](docs/cloudflare.md) for vulnerable DNS records
* take over vulnerable subdomains yourself before attackers and bug bounty researchers
* automatically create known issues in [Bugcrowd](docs/bugcrowd.md)
* vulnerable domains in Google Cloud DNS can be detected by [Domain Protect for GCP](https://github.com/ovotech/domain-protect-gcp)

### blog posts
* [How we prevented subdomain takeovers and saved $000s](https://tech.ovoenergy.com/how-we-prevented-subdomain-takeovers-and-saved-000s/)
* [OVO vs. Bug Bounty researchers - round 2](https://tech.ovoenergy.com/ovo-vs-bug-bounty-researchers-round-2/)

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

### or manually scan from your laptop

![Alt text](docs/images/vulnerable-eb-cnames.png?raw=true "Detect vulnerable ElasticBeanstalk CNAMEs")

## documentation
[Manual scans - AWS](manual-scans/aws/README.md)  
[Manual scans - CloudFlare](manual-scans/cloudflare/README.md)  
[Architecture](docs/architecture.md)  
[Database](docs/database.md)  
[Reports](docs/reports.md)  
[Automated takeover](docs/automated-takeover.md) *optional feature*  
[Cloudflare](docs/cloudflare.md) *optional feature*  
[Bugcrowd](docs/bugcrowd.md) *optional feature*  
[Vulnerability types](docs/vulnerability-types.md)  
[Vulnerable A records (IP addresses)](docs/a-records.md) *optional feature*   
[Requirements](docs/requirements.md)  
[Installation](docs/installation.md)  
[AWS IAM policies](docs/aws-iam-policies.md)  
[CI/CD](docs/ci-cd.md)  
[Development](docs/development.md)  
[Tests](docs/tests.md)  

## limitations
* this tool cannot guarantee 100% protection against subdomain takeover
* it currently only scans Amazon Route53 and Cloudflare, and only checks a limited number of takeover types
* vulnerable domains in Google Cloud DNS can be detected by [Domain Protect for GCP](https://github.com/ovotech/domain-protect-gcp)
