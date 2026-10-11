from __future__ import annotations

from enum import Enum


class ProtocolType(Enum):
    tcp = "0"
    udp = "1"
    unknownFutureValue = "2"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.ProtocolType"
