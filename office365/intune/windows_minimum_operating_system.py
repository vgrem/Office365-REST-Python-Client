from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class WindowsMinimumOperatingSystem(ClientValue):
    v10_0: bool | None = None
    v8_0: bool | None = None
    v8_1: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsMinimumOperatingSystem"
