import dns.resolver


def vulnerable_ns(domain_name):

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

    except (dns.resolver.NoAnswer, dns.resolver.Timeout):
        return False

    return False


def vulnerable_cname(domain_name):

    try:
        dns.resolver.resolve(domain_name, "A")
        return False

    except dns.resolver.NXDOMAIN:
        try:
            dns.resolver.resolve(domain_name, "CNAME")
            return True

        except dns.resolver.NoNameservers:
            return False

    except (dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.resolver.Timeout):
        return False


def vulnerable_alias(domain_name):

    try:
        dns.resolver.resolve(domain_name, "A")
        return False

    except dns.resolver.NoAnswer:
        return True

    except (dns.resolver.NoNameservers, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
        return False


def dns_deleted(domain_name):

    try:
        # RdataType 0 (NONE) to prevent false positives with CNAME vulnerabilities
        dns.resolver.resolve(domain_name, 0)

    except dns.resolver.NXDOMAIN:
        return True

    except (dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.resolver.Timeout):
        return False

    return False


def vulnerable_ns_update(domain_name):
    # used by update Lambda to check if a Vulnerable NS record has been fixed
    # same as vulnerable_ns except returns True if no answer or timeout

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

    except (dns.resolver.NoAnswer, dns.resolver.Timeout):
        return True

    return False
