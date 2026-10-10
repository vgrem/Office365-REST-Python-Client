from __future__ import annotations

from enum import Enum


class EvaluationOutcome(Enum):
    approved = "0"
    denied = "1"
    unknownFutureValue = "2"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EvaluationOutcome"
