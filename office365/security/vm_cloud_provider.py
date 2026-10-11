from __future__ import annotations

from enum import Enum


class VmCloudProvider(Enum):
    unknown = "0"
    azure = "1"
    unknownFutureValue = "15"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.VmCloudProvider"
