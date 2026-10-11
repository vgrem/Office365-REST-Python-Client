from __future__ import annotations

from enum import Enum


class HostReputationClassification(Enum):
    unknown = "0"
    neutral = "1"
    suspicious = "2"
    malicious = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.HostReputationClassification"
