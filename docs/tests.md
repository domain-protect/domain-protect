# Tests

* CircleCI pipeline includes Terraform format and Python tests using `Black` and `Prospector`
* If testing with `Prospector` locally, set your Python Path, e.g.
```
$ export PYTHONPATH="${PYTHONPATH}:/Users/paul/src/github.com/ovotech/domain-protect"
```
* to test Domain Protect functionality, use a test AWS Organization and test Cloudflare account
* for major changes, the following combinations of functionality should be tested:

|Vulnerability           |Detect |Takeover | Fixed |
|------------------------|:-:|:-:|:-:|
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

* select the links above to see details of DNS records to create for tests

[back to README](../README.md)