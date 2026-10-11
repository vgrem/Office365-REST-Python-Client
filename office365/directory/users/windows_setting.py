from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.users.windows_setting_instance import (
        WindowsSettingInstance,
    )
    from office365.directory.users.windowssettingtype import WindowsSettingType


class WindowsSetting(Entity):
    @property
    def payload_type(self) -> Optional[str]:
        """Gets the payloadType property"""
        return self.properties.get("payloadType", None)

    @property
    def setting_type(self) -> WindowsSettingType:
        """Gets the settingType property"""
        from office365.directory.users.windowssettingtype import WindowsSettingType

        return self.properties.get("settingType", WindowsSettingType.roaming)

    @property
    def windows_device_id(self) -> Optional[str]:
        """Gets the windowsDeviceId property"""
        return self.properties.get("windowsDeviceId", None)

    @property
    def instances(self) -> EntityCollection[WindowsSettingInstance]:
        """Gets the instances property"""
        from office365.directory.users.windows_setting_instance import (
            WindowsSettingInstance,
        )

        return self.properties.get(
            "instances",
            EntityCollection[WindowsSettingInstance](
                self.context, WindowsSettingInstance, ResourcePath("instances", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsSetting"
