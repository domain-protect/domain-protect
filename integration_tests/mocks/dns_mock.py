import dns


class DNSLookup:
    def __init__(self, name, content, exception=None, record_type="A") -> None:
        self.name = name
        self.content = content
        self.exception = exception
        self.record_type = record_type


class DNSMock:
    def __init__(self, patch) -> None:
        self.lookups = []
        self.patch = patch

    def add_lookup(self, name, content, exception=None, record_type="A"):
        self.lookups.append(DNSLookup(name, content, exception, record_type))

    def generate_lookup_function(self):
        def lookup(name, record_type="A"):
            record = next(
                filter(lambda f: f.name == name and f.record_type == record_type, self.lookups),
                DNSLookup(None, None, exception=dns.resolver.NoNameservers),
            )

            if record.exception is not None:
                raise record.exception

            return [record]

        return lookup
