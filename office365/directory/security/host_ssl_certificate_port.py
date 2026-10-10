from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class HostSslCertificatePort(ClientValue):
    firstSeenDateTime: datetime | None = None
    lastSeenDateTime: datetime | None = None
    port: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.HostSslCertificatePort"
