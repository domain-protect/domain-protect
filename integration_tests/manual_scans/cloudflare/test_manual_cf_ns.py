from unittest.mock import call, patch
import dns

from manual_scans.cloudflare.cf_ns import main


@patch("manual_scans.cloudflare.cf_ns.print_list")
def test_cf_ns_prints_ns_with_no_name_server(print_list_mock, cloudflare_mock, dns_mock):
    dns_mock.add_lookup("sub.ns.co.uk", "sub.ns.co.uk", exception=dns.resolver.NoNameservers, record_type="NS")

    cloudflare_mock.add_zone("test1.co.uk").add_dns("sub.ns.co.uk", "NS", "sub.ns.co.uk").build()

    main()

    print_list_mock.assert_called_once_with(["sub.ns.co.uk"])


@patch("manual_scans.cloudflare.cf_ns.print_list")
def test_cf_ns_ignores_a_records(print_list_mock, cloudflare_mock, dns_mock):
    cloudflare_mock.add_zone("test2.co.uk").add_dns("*.test2.co.uk", "A", "192.168.1.1").build()

    main()

    print_list_mock.assert_not_called()
    dns_mock.patch.assert_not_called()


@patch("manual_scans.cloudflare.cf_ns.print_list")
def test_cf_ns_ignores_ns_records_where_name_matches_zone(print_list_mock, cloudflare_mock, dns_mock):
    cloudflare_mock.add_zone("test2.co.uk").add_dns("test2.co.uk", "A", "192.168.1.1").build()

    main()

    print_list_mock.assert_not_called()
    dns_mock.patch.assert_not_called()


@patch("manual_scans.cloudflare.cf_ns.my_print")
def test_cf_prints_insecure_domains(my_print_mock, cloudflare_mock, dns_mock):
    dns_mock.add_lookup("sub.ns.co.uk", "sub.ns.co.uk", exception=dns.resolver.NoNameservers, record_type="A")

    cloudflare_mock.add_zone("test1.co.uk").add_dns("sub.ns.co.uk", "NS", "sub.ns.co.uk").build()

    main()

    expected_call = call("1. sub.ns.co.uk", "ERROR")
    my_print_mock.assert_has_calls([expected_call])


@patch("manual_scans.cloudflare.cf_ns.my_print")
def test_cf_prints_secure_domains(my_print_mock, cloudflare_mock, dns_mock):
    dns_mock.add_lookup("sub.ns.co.uk", "sub.ns.co.uk", exception=dns.resolver.NXDOMAIN, record_type="A")

    cloudflare_mock.add_zone("test1.co.uk").add_dns("sub.ns.co.uk", "NS", "sub.ns.co.uk").build()

    main()

    expected_call = call("1. sub.ns.co.uk", "SECURE")
    my_print_mock.assert_has_calls([expected_call])
