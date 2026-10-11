from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.security.threatintelligence.host_component import HostComponent


@dataclass
class HostPortComponent(ClientValue):
    firstSeenDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    isRecent: bool | None = None
    lastSeenDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    component: HostComponent | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.HostPortComponent"
