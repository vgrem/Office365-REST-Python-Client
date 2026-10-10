from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class AndroidMinimumOperatingSystem(ClientValue):
    v10_0: bool | None = None
    v11_0: bool | None = None
    v4_0: bool | None = None
    v4_0_3: bool | None = None
    v4_1: bool | None = None
    v4_2: bool | None = None
    v4_3: bool | None = None
    v4_4: bool | None = None
    v5_0: bool | None = None
    v5_1: bool | None = None
    v6_0: bool | None = None
    v7_0: bool | None = None
    v7_1: bool | None = None
    v8_0: bool | None = None
    v8_1: bool | None = None
    v9_0: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AndroidMinimumOperatingSystem"
