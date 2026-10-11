from __future__ import annotations

from dataclasses import dataclass, field

from office365.intune.devices.management.windows_device_account import (
    WindowsDeviceAccount,
)
from office365.runtime.client_value import ClientValue


@dataclass
class UpdateWindowsDeviceAccountActionParameter(ClientValue):
    calendarSyncEnabled: bool | None = None
    deviceAccount: WindowsDeviceAccount = field(default_factory=WindowsDeviceAccount)
    deviceAccountEmail: str | None = None
    exchangeServer: str | None = None
    passwordRotationEnabled: bool | None = None
    sessionInitiationProtocalAddress: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UpdateWindowsDeviceAccountActionParameter"
