from __future__ import annotations

from enum import Enum


class EventSource(Enum):
    system = "0"
    admin = "1"
    user = "2"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.EventSource"
