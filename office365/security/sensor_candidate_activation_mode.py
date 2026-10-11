from __future__ import annotations

from enum import Enum


class SensorCandidateActivationMode(Enum):
    manual = "1"
    automated = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.SensorCandidateActivationMode"
