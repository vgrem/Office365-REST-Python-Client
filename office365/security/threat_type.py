from __future__ import annotations

from enum import Enum


class ThreatType(Enum):
    unknown = "0"
    spam = "1"
    malware = "2"
    phish = "3"
    none = "4"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.ThreatType"
