from __future__ import annotations

from enum import Enum


class MaxWorkLocationDetails(Enum):
    unknown = "0"
    none = "1"
    approximate = "2"
    specific = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MaxWorkLocationDetails"
