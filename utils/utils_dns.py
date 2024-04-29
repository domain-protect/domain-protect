import sys

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
        # vulnerable domain
        return True

    except resolver.NoAnswer:
        # domain not vulnerable, no A record for domain
        return False

    except resolver.Timeout:
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

    except resolver.Timeout:
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

    except resolver.Timeout:
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


def updated_a_record(domain_name, ip_address):
    # returns first value only

    try:
        response = myresolver.resolve(domain_name, "A")

        for rdata in response:
            new_ip_address = rdata.to_text()
            if ip_address not in (new_ip_address, "test"):
                print(f"{domain_name} A record updated from {ip_address} to {new_ip_address}")

            return new_ip_address

    except (resolver.NoAnswer, resolver.NXDOMAIN):
        print(f"DNS A record for {domain_name} no longer found")
        return ip_address

    except (resolver.NoNameservers, resolver.NoResolverConfiguration, resolver.Timeout):
        return ip_address

    return ip_address


def firewall_test():
    result = updated_a_record("google.com", "test")

    if result == "test":
        print("No access to Google DNS servers, exiting")

        sys.exit()
