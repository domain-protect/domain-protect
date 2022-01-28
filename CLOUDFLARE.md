# Cloudflare

## Supported DNS vulnerability types
* NS subdomains
* CNAMEs pointing to missing resources, e.g. Elastic Beanstalk, Azure storage
* Cloudflare proxy configured with S3 origin in Free plan, directs to non-existent S3 bucket matching domain name

## Cloudflare manual scans
* scan your Cloudflare environment from a laptop
* details at [Cloudflare manual scans](manual-scans-cloudflare/README.md)

## Notifications from scheduled lambda function scans
![Alt text](images/cloudflare-slack.png?raw=true "Cloudflare API token creation")
* Receive alerts by Slack or email

## Automated takeover
Supported resource types detailed in [takeover](TAKEOVER.md):
* S3 buckets
* Elastic Beanstalk environments

## How to enable Cloudflare lambda functions
* By default Cloudflare lambda functions are not deployed
* to enable, set environment variable `cloudflare = true` in tfvars file or CI/CD pipeline

## Cloudflare API token
* required for Lambda functions to interact with Cloudflare
* log in to the Cloudflare console with a service account identity
* go to My Profile, API Tokens, Create Token
* At API Tokens, Create Token
* At Create Custom Token press Get Started
![Alt text](images/cloudflare-api-token.png?raw=true "Cloudflare API token creation")
* Give the API token a suitable name, e.g. domain-protect
* At permissions, choose Zone, DNS, read
* At Zone Resources, include all zones
* Press Continue to summary
![Alt text](images/cloudflare-api-token-summary.png?raw=true "Cloudflare API token creation")
* Press Create Token
* Copy token and save securely
* Set token as environment variable `cf_api_key = "xxxxxx"` in tfvars file or CI/CD pipeline

