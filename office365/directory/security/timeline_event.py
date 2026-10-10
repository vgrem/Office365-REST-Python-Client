from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


@dataclass
class TimelineEvent(ClientValue):
    eventDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    eventDetails: str | None = None
    eventResult: str | None = None
    eventThreats: StringCollection = field(default_factory=StringCollection)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.TimelineEvent"
