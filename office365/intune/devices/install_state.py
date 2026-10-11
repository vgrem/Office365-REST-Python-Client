from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.managed.ebook.installstate import (
        InstallState,
    )


class DeviceInstallState(Entity):
    @property
    def device_id(self) -> Optional[str]:
        """Gets the deviceId property"""
        return self.properties.get("deviceId", None)

    @property
    def device_name(self) -> Optional[str]:
        """Gets the deviceName property"""
        return self.properties.get("deviceName", None)

    @property
    def error_code(self) -> Optional[str]:
        """Gets the errorCode property"""
        return self.properties.get("errorCode", None)

    @property
    def install_state(self) -> InstallState:
        """Gets the installState property"""
        from office365.intune.devices.management.managed.ebook.installstate import (
            InstallState,
        )

        return self.properties.get("installState", InstallState.notApplicable)

    @property
    def last_sync_date_time(self) -> Optional[datetime]:
        """Gets the lastSyncDateTime property"""
        return self.properties.get("lastSyncDateTime", datetime.min)

    @property
    def os_description(self) -> Optional[str]:
        """Gets the osDescription property"""
        return self.properties.get("osDescription", None)

    @property
    def os_version(self) -> Optional[str]:
        """Gets the osVersion property"""
        return self.properties.get("osVersion", None)

    @property
    def user_name(self) -> Optional[str]:
        """Gets the userName property"""
        return self.properties.get("userName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceInstallState"
