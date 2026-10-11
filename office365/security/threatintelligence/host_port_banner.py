from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class HostPortBanner(ClientValue):
    banner: str | None = None
    firstSeenDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    lastSeenDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    scanProtocol: str | None = None
    timesObserved: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.HostPortBanner"
