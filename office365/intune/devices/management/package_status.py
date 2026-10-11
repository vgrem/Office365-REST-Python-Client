from __future__ import annotations

from enum import Enum


class PackageStatus(Enum):
    none = "0"
    some = "1"
    all = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PackageStatus"
