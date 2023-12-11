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
                            }
                        ],
                    },
                },
            ],
        },
    )
