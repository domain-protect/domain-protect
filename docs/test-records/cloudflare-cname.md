# Cloudflare CNAME
* Cloudflare, select site, DNS
* example record for testing CNAME to root (apex) domain
* leave Proxy on
* For the name, use `@` to create the apex domain record
* For the content, enter an existing public bucket FQDN 

![Alt text](images/cloudflare-s3.png?raw=true "Example DNS record")

* refer to the first entry in the image

|Type|Name|Content|Proxy Status|TTL|
|----|----|-------|------------|---|
|CNAME|thehappycloud.co|s3-public-bucket-policy.s3.eu-west-1.amazonaws.com|Proxied|Auto|

[Back to Tests](..\tests.md)