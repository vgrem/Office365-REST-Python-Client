from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class HostSecurityState(ClientValue):
    fqdn: str | None = None
    isAzureAdJoined: bool | None = None
    isAzureAdRegistered: bool | None = None
    isHybridAzureDomainJoined: bool | None = None
    netBiosName: str | None = None
    os: str | None = None
    privateIpAddress: str | None = None
    publicIpAddress: str | None = None
    riskScore: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.HostSecurityState"
