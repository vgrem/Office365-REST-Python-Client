from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.configurations.windows.windowsusertype import (
    WindowsUserType,
)
from office365.intune.devices.management.managed.windows.usagetype import (
    WindowsDeviceUsageType,
)
from office365.runtime.client_value import ClientValue


@dataclass
class OutOfBoxExperienceSetting(ClientValue):
    deviceUsageType: WindowsDeviceUsageType = WindowsDeviceUsageType.singleUser
    escapeLinkHidden: bool | None = None
    eulaHidden: bool | None = None
    keyboardSelectionPageSkipped: bool | None = None
    privacySettingsHidden: bool | None = None
    userType: WindowsUserType = WindowsUserType.administrator

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OutOfBoxExperienceSetting"
