from dns import resolver

# Google public DNS servers
nameservers = ["8.8.8.8", "8.8.4.4"]
myresolver = resolver.Resolver()
myresolver.nameservers = nameservers


def vulnerable_ns(domain_name, update_scan=False):

    try:
        # A record lookup detects name servers not configured for domain
        myresolver.resolve(domain_name, "A")

    except resolver.NXDOMAIN:
        # domain does not exist
        return False

    except resolver.NoNameservers:
        # vulneable domain
        return True

    except resolver.NoAnswer:
        # domain not vulnerable, no A record for domain
        return False

    except (resolver.Timeout):
        if update_scan:
            # prevents reporting as fixed when DNS query timeout
            return True

        return False

    except Exception as e:
        # catch any unhandled exceptions in Lambda logs
        if update_scan:
            print(f"Unhandled exception testing DNS for NS records during update scan: {e}")
            return True

        print(f"Unhandled exception testing DNS for NS records during standard scan: {e}")

    return False


def vulnerable_cname(domain_name, update_scan=False):

    try:
        myresolver.resolve(domain_name, "A")
        return False

    except resolver.NXDOMAIN:
        try:
            myresolver.resolve(domain_name, "CNAME")
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
        myresolver.resolve(domain_name, "A")
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
        myresolver.resolve(domain_name, record_type)

    except (resolver.NoAnswer, resolver.NXDOMAIN):
        print(f"DNS {record_type} record for {domain_name} no longer found")
        return True

    except (resolver.NoNameservers, resolver.NoResolverConfiguration, resolver.Timeout):
        return False

    return False
