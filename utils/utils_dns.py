import dns.resolver


def vulnerable_ns(domain_name, update_scan=False):

    my_resolver = dns.resolver.Resolver()

    # Google public DNS server to prevent AWS NS vulnerabilities occasionally being incorrectly reported as fixed
    my_resolver.nameservers = ["8.8.8.8"]

    try:
        dns.resolver.resolve(domain_name)

    except dns.resolver.NXDOMAIN:
        return False

    except dns.resolver.NoNameservers:

        try:
            ns_records = dns.resolver.resolve(domain_name, "NS")
            if len(ns_records) == 0:
                return True

        except dns.resolver.NoNameservers:
            return True

    except dns.resolver.NoAnswer:
        return False

    except (dns.resolver.Timeout):
        if update_scan:
            return True

        return False

    except Exception as e:

        if update_scan:
            print(f"Unhandled exception testing DNS for NS records during update scan: {e}")
            return True

        print(f"Unhandled exception testing DNS for NS records during standard scan: {e}")

    return False


def vulnerable_cname(domain_name, update_scan=False):

    try:
        dns.resolver.resolve(domain_name, "A")
        return False

    except dns.resolver.NXDOMAIN:
        try:
            dns.resolver.resolve(domain_name, "CNAME")
            return True

        except dns.resolver.NoNameservers:
            return False

    except (dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return False

    except (dns.resolver.Timeout):
        if update_scan:
            return True

        return False

    except Exception as e:

        if update_scan:
            print(f"Unhandled exception testing DNS for NS records during update scan: {e}")
            return True

        print(f"Unhandled exception testing DNS for NS records during standard scan: {e}")

    return False


def vulnerable_alias(domain_name, update_scan=False):

    try:
        dns.resolver.resolve(domain_name, "A")
        return False

    except dns.resolver.NoAnswer:
        return True

    except (dns.resolver.NoNameservers, dns.resolver.NXDOMAIN):
        return False

    except (dns.resolver.Timeout):
        if update_scan:
            return True

        return False


def dns_deleted(domain_name, record_type="A"):
    # DNS record type examples: A, CNAME, MX, NS

    try:
        dns.resolver.resolve(domain_name, record_type)

    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        print(f"DNS {type} record for {domain_name} no longer found")
        return True

    except (dns.resolver.NoNameservers, dns.resolver.NoResolverConfiguration, dns.resolver.Timeout):
        return False

    return False
