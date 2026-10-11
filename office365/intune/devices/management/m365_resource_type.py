from __future__ import annotations

from enum import Enum


class M365ResourceType(Enum):
    none = "0"
    group = "1"
    user = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.M365ResourceType"
