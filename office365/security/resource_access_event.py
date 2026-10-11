from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class ResourceAccessEvent(ClientValue):
    accessDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    accountId: str | None = None
    ipAddress: str | None = None
    resourceIdentifier: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.ResourceAccessEvent"
