from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class DeviceOperatingSystemSummary(ClientValue):
    androidCorporateWorkProfileCount: int | None = None
    androidCount: int | None = None
    androidDedicatedCount: int | None = None
    androidDeviceAdminCount: int | None = None
    androidFullyManagedCount: int | None = None
    androidWorkProfileCount: int | None = None
    configMgrDeviceCount: int | None = None
    iosCount: int | None = None
    macOSCount: int | None = None
    unknownCount: int | None = None
    windowsCount: int | None = None
    windowsMobileCount: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceOperatingSystemSummary"
