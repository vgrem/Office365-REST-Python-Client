from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class MacOSMinimumOperatingSystem(ClientValue):
    v10_10: bool | None = None
    v10_11: bool | None = None
    v10_12: bool | None = None
    v10_13: bool | None = None
    v10_14: bool | None = None
    v10_15: bool | None = None
    v10_7: bool | None = None
    v10_8: bool | None = None
    v10_9: bool | None = None
    v11_0: bool | None = None
    v12_0: bool | None = None
    v13_0: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MacOSMinimumOperatingSystem"
