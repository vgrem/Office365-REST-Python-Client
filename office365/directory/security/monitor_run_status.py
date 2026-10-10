from __future__ import annotations

from enum import Enum


class MonitorRunStatus(Enum):
    successful = "0"
    partiallySuccessful = "1"
    failed = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MonitorRunStatus"
