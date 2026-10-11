from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.security.alerts.connection_direction import ConnectionDirection
from office365.security.alerts.connectionstatus import ConnectionStatus
from office365.security.alerts.securitynetworkprotocol import (
    SecurityNetworkProtocol,
)


@dataclass
class NetworkConnection(ClientValue):
    applicationName: str | None = None
    destinationAddress: str | None = None
    destinationDomain: str | None = None
    destinationLocation: str | None = None
    destinationPort: str | None = None
    destinationUrl: str | None = None
    direction: ConnectionDirection = ConnectionDirection.unknown
    domainRegisteredDateTime: datetime | None = None
    localDnsName: str | None = None
    natDestinationAddress: str | None = None
    natDestinationPort: str | None = None
    natSourceAddress: str | None = None
    natSourcePort: str | None = None
    protocol: SecurityNetworkProtocol = SecurityNetworkProtocol.unknown
    riskScore: str | None = None
    sourceAddress: str | None = None
    sourceLocation: str | None = None
    sourcePort: str | None = None
    status: ConnectionStatus = ConnectionStatus.unknown
    urlParameters: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.NetworkConnection"
