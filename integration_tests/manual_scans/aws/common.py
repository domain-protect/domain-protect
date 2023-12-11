def setup_hosted_zone(moto_route53, dns_name):
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
                            "DNSName": dns_name,
                            "EvaluateTargetHealth": False,
                        },
                    },
                },
            ],
        },
    )
