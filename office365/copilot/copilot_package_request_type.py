from __future__ import annotations

from enum import Enum


class CopilotPackageRequestType(Enum):
    publish = "0"
    activate = "1"
    access = "2"
    update = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CopilotPackageRequestType"
