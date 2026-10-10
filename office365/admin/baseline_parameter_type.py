from __future__ import annotations

from enum import Enum


class BaselineParameterType(Enum):
    string = "0"
    integer = "1"
    boolean = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BaselineParameterType"
