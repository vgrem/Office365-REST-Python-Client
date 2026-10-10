from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.configurations.ios.iosnotificationalerttype import (
    IosNotificationAlertType,
)
from office365.runtime.client_value import ClientValue


@dataclass
class IosNotificationSettings(ClientValue):
    alertType: IosNotificationAlertType = IosNotificationAlertType.deviceDefault
    appName: str | None = None
    badgesEnabled: bool | None = None
    bundleID: str | None = None
    enabled: bool | None = None
    publisher: str | None = None
    showInNotificationCenter: bool | None = None
    showOnLockScreen: bool | None = None
    soundsEnabled: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosNotificationSettings"
