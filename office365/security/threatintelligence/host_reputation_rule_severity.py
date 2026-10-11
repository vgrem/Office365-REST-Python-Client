from __future__ import annotations

from enum import Enum


class HostReputationRuleSeverity(Enum):
    unknown = "0"
    low = "1"
    medium = "2"
    high = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.HostReputationRuleSeverity"
