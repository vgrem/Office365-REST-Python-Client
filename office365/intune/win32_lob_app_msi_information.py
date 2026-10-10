from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.management.mobileapps.win32.msipackagetype import (
    Win32LobAppMsiPackageType,
)
from office365.runtime.client_value import ClientValue


@dataclass
class Win32LobAppMsiInformation(ClientValue):
    packageType: Win32LobAppMsiPackageType = Win32LobAppMsiPackageType.perMachine
    productCode: str | None = None
    productName: str | None = None
    productVersion: str | None = None
    publisher: str | None = None
    requiresReboot: bool | None = None
    upgradeCode: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Win32LobAppMsiInformation"
