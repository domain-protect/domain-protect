import uuid


class Zone:
    def __init__(self, name) -> None:
        self.Name = name
        self.Id = uuid.uuid4().hex
        self.dns_records = []


class DNSRecord:
    def __init__(self, name, record_type, value) -> None:
        self.Name = name
        self.Type = record_type
        self.Content = value
        self.Id = uuid.uuid4().hex


class CloudFlareDnsMock:
    def __init__(self, zone_data) -> None:
        self._zone_data = zone_data

    # pylint: disable=unused-argument
    def get(self, zone_id, params):
        zone = next(filter(lambda z: z.Id == zone_id, self._zone_data))
        records = [{"id": r.Id, "name": r.Name, "type": r.Type, "content": r.Content} for r in zone.dns_records]
        return {"result": records, "result_info": {"total_pages": 1}}


class CloudFlareZoneMock:
    def __init__(self, zone_data) -> None:
        self._zone_data = zone_data
        self.dns_records = CloudFlareDnsMock(zone_data)

    # pylint: disable=unused-argument
    def get(self, params):
        zones = [{"id": zone.Id, "name": zone.Name} for zone in self._zone_data]
        return {"result": zones, "result_info": {"total_pages": 1}}


class CloudFlareMock:
    def __init__(self) -> None:
        self._zone_data = []
        self.zones = CloudFlareZoneMock(self._zone_data)

    def add_zone(self, name):
        return ZoneGenerator(name, self)

    def append_zone(self, zone):
        self._zone_data.append(zone)


class ZoneGenerator:
    def __init__(self, name, cf_mock) -> None:
        self._cf_mock = cf_mock
        self.zone = Zone(name)

    def add_dns(self, name, record_type, content):
        self.zone.dns_records.append(DNSRecord(name, record_type, content))
        return self

    def build(self):
        self._cf_mock.append_zone(self.zone)
