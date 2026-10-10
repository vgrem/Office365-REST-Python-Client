from __future__ import annotations

from enum import Enum


class CopilotPackageRequestStatus(Enum):
    pending = "0"
    approved = "1"
    rejected = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CopilotPackageRequestStatus"
