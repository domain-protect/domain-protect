# A Record - Global Accelerator IP addresses
* ensure that an IP address scan has completed and there is at least one IP address in the IP address database
* download the [latest list of Amazon IP addresses](https://ip-ranges.amazonaws.com/ip-ranges.json)
* select two IPv4 addresses in a network with `"service": "GLOBALACCELERATOR"` not already in use within the organisation
* create A record pointing to both IP addresses in Route53

<img src="images/a-globalaccelerator.png" width="300">

[Back to Manual Tests](../manual-tests.md)
