from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class VppLicensingType(ClientValue):
    supportsDeviceLicensing: bool | None = None
    supportsUserLicensing: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VppLicensingType"
