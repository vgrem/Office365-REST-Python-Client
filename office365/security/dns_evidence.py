from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.ip_evidence import IpEvidence


@dataclass
class DnsEvidence(ClientValue):
    domainName: str | None = None
    dnsServerIp: IpEvidence = field(default_factory=IpEvidence)
    hostIpAddress: IpEvidence = field(default_factory=IpEvidence)
    ipAddresses: ClientValueCollection[IpEvidence] = field(default_factory=lambda: ClientValueCollection(IpEvidence))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.DnsEvidence"
