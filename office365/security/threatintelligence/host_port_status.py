from __future__ import annotations

from enum import Enum


class HostPortStatus(Enum):
    open = "0"
    filtered = "1"
    closed = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.HostPortStatus"
