from __future__ import annotations

from enum import Enum


class ErrorCorrectionLevel(Enum):
    m = "2"
    q = "3"
    h = "4"
    unknownFutureValue = "5"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ErrorCorrectionLevel"

    l_ = "1"
