from __future__ import annotations

from enum import Enum


class WifiBand(Enum):
    unknown = "0"
    frequency24GHz = "1"
    frequency50GHz = "2"
    frequency60GHz = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.WifiBand"
