from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class IosMinimumOperatingSystem(ClientValue):
    v10_0: bool | None = None
    v11_0: bool | None = None
    v12_0: bool | None = None
    v13_0: bool | None = None
    v14_0: bool | None = None
    v15_0: bool | None = None
    v8_0: bool | None = None
    v9_0: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosMinimumOperatingSystem"
