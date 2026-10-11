from __future__ import annotations

from enum import Enum


class IntelligenceProfileKind(Enum):
    actor = "0"
    tool = "1"
    unknownFutureValue = "2"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.IntelligenceProfileKind"
