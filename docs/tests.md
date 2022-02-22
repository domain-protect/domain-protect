# testing

* CircleCI pipeline includes Terraform format and Python tests
* to test Domain Protect functionality, use a test AWS Organization and test Cloudflare account
* for major changes, the following combinations of functionality should be tested:

|Vulnerability           |Detect |Takeover | Fixed |
|------------------------|:-:|:-:|:-:|
|Alias CloudFront S3     |X|X|X|
|Alias Elastic Beanstalk |X|X|X|
|Alias S3                |X|X|X|
|CNAME Azure             |X|N/A|X|
|CNAME CloudFront S3     |X|X|X|
|CNAME Elastic Beanstalk |X|X|X|
|CNAME Google            |X|N/A|X|
|CNAME S3                |X|X|X|
|NS Subdomain            |X|N/A|X|
|NS Domain               |X|N/A|X|
|CloudFlare NS           |X|N/A|X|
|CloudFlare Azure        |X|N/A|X|
|Cloudflare S3           |X|X|X|
|Cloudflare CNAME        |X|N/A|X|
