# Cloudflare S3
* Cloudflare, select site, DNS
* example record for testing CNAME to missing S3 bucket

![Alt text](images/cloudflare-s3.png?raw=true "Example DNS record")

* refer to the second entry in the image

|Type|Name|Content|Proxy Status|TTL|
|----|----|-------|------------|---|
|CNAME|vulnerable-cname|vulnerable-cname.thehappycloud.co|DNS only|Auto|

[Back to Manual Tests](../manual-tests.md)