from __future__ import annotations

from enum import Enum


class IndicatorSource(Enum):
    microsoft = "0"
    osint = "1"
    public = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.IndicatorSource"
