from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.security.ip_evidence import IpEvidence
from office365.security.protocol_type import ProtocolType


@dataclass
class NetworkConnectionEvidence(ClientValue):
    destinationAddress: IpEvidence = field(default_factory=IpEvidence)
    destinationPort: int | None = None
    sourceAddress: IpEvidence = field(default_factory=IpEvidence)
    sourcePort: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.NetworkConnectionEvidence"

    protocol: ProtocolType = ProtocolType.tcp
