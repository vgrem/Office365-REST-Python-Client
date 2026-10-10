from __future__ import annotations

from enum import Enum


class SystemBrowserEnabledOn(Enum):
    none = "0"
    ios = "1"
    android = "2"
    mac = "4"
    unknownFutureValue = "16"
    linux = "8"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SystemBrowserEnabledOn"
