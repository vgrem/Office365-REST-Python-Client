from __future__ import annotations

from enum import Enum


class EnrollmentState(Enum):
    unknown = "0"
    enrolled = "1"
    pendingReset = "2"
    failed = "3"
    notContacted = "4"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EnrollmentState"
