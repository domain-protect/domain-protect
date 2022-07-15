from unittest.mock import patch
import dns

from manual_scans.cloudflare.cf_ns import main


@patch("manual_scans.cloudflare.cf_ns.print_list")
def test_cf_ns_detects_ns_with_no_name_server(print_list_mock, cloudflare_mock, dns_mock):
    dns_mock.add_lookup("sub.ns.co.uk", "sub.ns.co.uk", exception=dns.resolver.NoNameservers)

    cloudflare_mock.add_zone("test1.co.uk").add_dns("test1.co.uk", "NS", "ns.test.co.uk").add_dns(
        "sub.ns.co.uk", "NS", "sub.ns.co.uk"
    ).build()
    cloudflare_mock.add_zone("test2.co.uk").add_dns("*.test2.co.uk", "A", "192.168.1.1").build()

    main()

    print_list_mock.assert_called_once_with(["sub.ns.co.uk"])
