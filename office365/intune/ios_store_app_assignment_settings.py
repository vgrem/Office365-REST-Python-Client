from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class IosStoreAppAssignmentSettings(ClientValue):
    isRemovable: bool | None = None
    uninstallOnDeviceRemoval: bool | None = None
    vpnConfigurationId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosStoreAppAssignmentSettings"
