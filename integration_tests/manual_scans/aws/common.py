def setup_cloudfront_distribution_with_origin_url(moto_cloudfront, origin_domain_name, is_s3=True):
    # NOTE: All the fields below are required
    config = {
        "Origins": {
            "Quantity": 1,
            "Items": [
                {
                    "Id": "MyOrigin",
                    "DomainName": origin_domain_name,
                    "S3OriginConfig": {
                        "OriginAccessIdentity": "",
                    },
                },
            ],
        },
        "Enabled": True,
        "Comment": "test",
        "CallerReference": "test",
        "Aliases": {
            "Quantity": 2,
            "Items": [
                "vulnerable.domain-protect.com",
                "something.else.com",
            ],
        },
        "DefaultCacheBehavior": {
            "AllowedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"],
                "CachedMethods": {
                    "Quantity": 2,
                    "Items": ["GET", "HEAD"],
                },
            },
            "ViewerProtocolPolicy": "allow-all",
            "TargetOriginId": "MyOrigin",
            "ForwardedValues": {
                "QueryString": False,
                "Cookies": {
                    "Forward": "none",
                },
            },
        },
    }
    if not is_s3:
        del config["Origins"]["Items"][0]["S3OriginConfig"]
        config["Origins"]["Items"][0]["CustomOriginConfig"] = {
            "HTTPPort": 80,
            "HTTPSPort": 443,
            "OriginProtocolPolicy": "http-only",
        }

    distribution = moto_cloudfront.create_distribution(DistributionConfig=config)

    # NOTE: From moto's documentation, this list_distributions() call is needed to "advance" the distribution to a deployed state
    distributions = moto_cloudfront.list_distributions()
    return distributions["DistributionList"]["Items"][0]


def setup_hosted_zone_with_alias(moto_route53, target_dns_name):
    hosted_zone = moto_route53.create_hosted_zone(
        Name="domain-protect.com",
        CallerReference="123abc",
        HostedZoneConfig={"Comment": "", "PrivateZone": False},
    )
    moto_route53.change_resource_record_sets(
        HostedZoneId=hosted_zone["HostedZone"]["Id"],
        ChangeBatch={
            "Comment": "Create alias record set",
            "Changes": [
                {
                    "Action": "CREATE",
                    "ResourceRecordSet": {
                        "Name": "vulnerable.domain-protect.com",
                        "Type": "A",
                        "AliasTarget": {
                            "HostedZoneId": hosted_zone["HostedZone"]["Id"],
                            "DNSName": target_dns_name,
                            "EvaluateTargetHealth": False,
                        },
                    },
                },
            ],
        },
    )


def setup_hosted_zone_with_cname(moto_route53, target_dns_name):
    hosted_zone = moto_route53.create_hosted_zone(
        Name="domain-protect.com",
        CallerReference="123abc",
        HostedZoneConfig={"Comment": "", "PrivateZone": False},
    )
    moto_route53.change_resource_record_sets(
        HostedZoneId=hosted_zone["HostedZone"]["Id"],
        ChangeBatch={
            "Comment": "Create CNAME record set",
            "Changes": [
                {
                    "Action": "CREATE",
                    "ResourceRecordSet": {
                        "Name": "vulnerable.domain-protect.com",
                        "Type": "CNAME",
                        "ResourceRecords": [
                            {
                                "Value": target_dns_name,
                            },
                        ],
                    },
                },
            ],
        },
    )
