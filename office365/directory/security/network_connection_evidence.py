from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.ip_evidence import IpEvidence
from office365.runtime.client_value import ClientValue


@dataclass
class NetworkConnectionEvidence(ClientValue):
    destinationAddress: IpEvidence = field(default_factory=IpEvidence)
    destinationPort: int | None = None
    sourceAddress: IpEvidence = field(default_factory=IpEvidence)
    sourcePort: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.NetworkConnectionEvidence"
