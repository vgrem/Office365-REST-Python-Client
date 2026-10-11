from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.install_state import DeviceInstallState


class UserInstallStateSummary(Entity):
    @property
    def failed_device_count(self) -> Optional[int]:
        """Gets the failedDeviceCount property"""
        return self.properties.get("failedDeviceCount", None)

    @property
    def installed_device_count(self) -> Optional[int]:
        """Gets the installedDeviceCount property"""
        return self.properties.get("installedDeviceCount", None)

    @property
    def not_installed_device_count(self) -> Optional[int]:
        """Gets the notInstalledDeviceCount property"""
        return self.properties.get("notInstalledDeviceCount", None)

    @property
    def user_name(self) -> Optional[str]:
        """Gets the userName property"""
        return self.properties.get("userName", None)

    @property
    def device_states(self) -> EntityCollection[DeviceInstallState]:
        """Gets the deviceStates property"""
        from office365.intune.devices.install_state import DeviceInstallState

        return self.properties.get(
            "deviceStates",
            EntityCollection[DeviceInstallState](
                self.context, DeviceInstallState, ResourcePath("deviceStates", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserInstallStateSummary"
