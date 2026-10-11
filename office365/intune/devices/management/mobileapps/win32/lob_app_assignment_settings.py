from __future__ import annotations

from dataclasses import dataclass, field

from office365.intune.devices.management.mobileapps.mobile_app_install_time_settings import (
    MobileAppInstallTimeSettings,
)
from office365.intune.devices.management.mobileapps.win32.deliveryoptimizationpriority import (
    Win32LobAppDeliveryOptimizationPriority,
)
from office365.intune.devices.management.mobileapps.win32.lob_app_auto_update_settings import (
    Win32LobAppAutoUpdateSettings,
)
from office365.intune.devices.management.mobileapps.win32.lob_app_restart_settings import (
    Win32LobAppRestartSettings,
)
from office365.intune.devices.management.mobileapps.win32.notification import (
    Win32LobAppNotification,
)
from office365.runtime.client_value import ClientValue


@dataclass
class Win32LobAppAssignmentSettings(ClientValue):
    autoUpdateSettings: Win32LobAppAutoUpdateSettings = field(default_factory=Win32LobAppAutoUpdateSettings)
    deliveryOptimizationPriority: Win32LobAppDeliveryOptimizationPriority = (
        Win32LobAppDeliveryOptimizationPriority.notConfigured
    )
    installTimeSettings: MobileAppInstallTimeSettings = field(default_factory=MobileAppInstallTimeSettings)
    notifications: Win32LobAppNotification = Win32LobAppNotification.showAll
    restartSettings: Win32LobAppRestartSettings = field(default_factory=Win32LobAppRestartSettings)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Win32LobAppAssignmentSettings"
