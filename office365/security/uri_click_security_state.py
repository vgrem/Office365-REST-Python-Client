from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class UriClickSecurityState(ClientValue):
    clickAction: str | None = None
    clickDateTime: datetime | None = None
    id: str | None = None
    sourceId: str | None = None
    uriDomain: str | None = None
    verdict: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UriClickSecurityState"
