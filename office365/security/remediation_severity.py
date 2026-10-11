from __future__ import annotations

from enum import Enum


class RemediationSeverity(Enum):
    low = "1"
    medium = "2"
    high = "3"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.RemediationSeverity"
