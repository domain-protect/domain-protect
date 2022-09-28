import dns.resolver

# Google public DNS servers
nameservers = ["8.8.8.8", "8.8.4.4"]
resolver = dns.resolver
resolver.resolve.nameservers = nameservers


def vulnerable_ns(domain_name, update_scan=False):

    try:
        resolver.resolve(domain_name, "NS")

    except resolver.NXDOMAIN:
        return False

    except resolver.NoNameservers:
        return True

    except resolver.NoAnswer:
        if update_scan:
            return True
        return False

    except (resolver.Timeout):
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
        resolver.resolve(domain_name, "A")
        return False

    except resolver.NXDOMAIN:
        try:
            resolver.resolve(domain_name, "CNAME")
            return True

        except resolver.NoNameservers:
            return False

    except (resolver.NoAnswer, resolver.NoNameservers):
        return False

    except (resolver.Timeout):
        if update_scan:
            return True

        return False

    except Exception as e:

        if update_scan:
            print(f"Unhandled exception testing DNS for CNAME records during update scan: {e}")
            return True

        print(f"Unhandled exception testing DNS for CNAME records during standard scan: {e}")

    return False


def vulnerable_alias(domain_name, update_scan=False):

    try:
        resolver.resolve(domain_name, "A")
        return False

    except resolver.NoAnswer:
        return True

    except (resolver.NoNameservers, resolver.NXDOMAIN):
        return False

    except (resolver.Timeout):
        if update_scan:
            return True

        return False


def dns_deleted(domain_name, record_type="A"):
    # DNS record type examples: A, CNAME, MX, NS

    try:
        resolver.resolve(domain_name, record_type)

    except (resolver.NoAnswer, resolver.NXDOMAIN):
        print(f"DNS {record_type} record for {domain_name} no longer found")
        return True

    except (resolver.NoNameservers, resolver.NoResolverConfiguration, resolver.Timeout):
        return False

    return False
