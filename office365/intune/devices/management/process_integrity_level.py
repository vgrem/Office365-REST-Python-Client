from __future__ import annotations

from enum import Enum


class ProcessIntegrityLevel(Enum):
    unknown = "0"
    untrusted = "1"
    low = "2"
    medium = "3"
    high = "4"
    system = "5"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ProcessIntegrityLevel"
