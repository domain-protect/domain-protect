# Tests

* GitHub Actions pipeline includes tests using:
```
bandit
black
checkov
prospector
terraform fmt
```
* if testing with `Prospector` locally, set your Python Path, e.g.
```
$ export PYTHONPATH="${PYTHONPATH}:/Users/paul/src/github.com/ovotech/domain-protect"
```
* test Terraform locally using Checkov:
```
checkov --config-file .config/sast_terraform_checkov_cli.yml --directory .
```
* to test Domain Protect functionality, use a test AWS Organization and test Cloudflare account
* for major changes, the following combinations of functionality should be tested:

|Vulnerability           |Detect |Takeover | Fixed |
|------------------------|:-:|:-:|:-:|
|[A record Elastic IP / EC2](test-records/a-eip.md)     |X|N/A|X|
|[A record Global Accelerator](test-records/a-globalaccelerator.md)     |X|N/A|X|
|[Alias CloudFront S3](test-records/alias-cloudfront.md)     |X|X|X|
|[Alias Elastic Beanstalk](test-records/alias-eb.md) |X|X|X|
|[Alias S3](test-records/alias-s3.md)|X|X|X|
|[CNAME Azure](test-records/cname-azure.md)|X|N/A|X|
|[CNAME CloudFront S3](test-records/cname-cloudfront.md)|X|X|X|
|[CNAME Elastic Beanstalk](test-records/cname-eb.md) |X|X|X|
|[CNAME Google](test-records/cname-google.md)            |X|N/A|X|
|[CNAME S3](test-records/cname-s3.md) |X|X|X|
|[NS Subdomain](test-records/ns-subdomain.md)|X|N/A|X|
|[NS Domain](test-records/ns-domain.md)|X|N/A|X|
|[CloudFlare Azure](test-records/cloudflare-azure.md)|X|N/A|X|
|[Cloudflare CNAME](test-records/cloudflare-cname.md)|X|X|X|
|[Cloudflare Elastic Beanstalk](test-records/cloudflare-eb.md)|X|X|X|
|[CloudFlare NS](test-records/cloudflare-ns.md)|X|N/A|X|
|[Cloudflare S3](test-records/cloudflare-s3.md)|X|X|X|

* select links above to see details of DNS records to create for tests

* test with optional features enabled and disabled in Terraform:

| Optional features |Enabled |Disabled |
|-------------------|:-:|:-:|
| [A records (IP addresses)](a-records.md)| X | X |
| [Takeover](automated-takeover.md)| X | X |
| [Cloudflare](cloudflare.md)| X | X |
| [Bugcrowd](bugcrowd.md)| X | X |

* select links above for details on enabling or disabling optional features

[back to README](../README.md)