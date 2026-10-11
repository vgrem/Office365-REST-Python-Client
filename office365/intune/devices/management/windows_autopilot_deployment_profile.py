from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.intune.devices.configurations.windows.out_of_box_experience_setting import OutOfBoxExperienceSetting
    from office365.intune.devices.management.managed.windows.autopilot_device_type import (
        WindowsAutopilotDeviceType,
    )
    from office365.intune.devices.management.windows_autopilot_device_identity import (
        WindowsAutopilotDeviceIdentity,
    )


class WindowsAutopilotDeploymentProfile(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def device_name_template(self) -> Optional[str]:
        """Gets the deviceNameTemplate property"""
        return self.properties.get("deviceNameTemplate", None)

    @property
    def device_type(self) -> WindowsAutopilotDeviceType:
        """Gets the deviceType property"""
        from office365.intune.devices.management.managed.windows.autopilot_device_type import (
            WindowsAutopilotDeviceType,
        )

        return self.properties.get("deviceType", WindowsAutopilotDeviceType.windowsPc)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def hardware_hash_extraction_enabled(self) -> Optional[bool]:
        """Gets the hardwareHashExtractionEnabled property"""
        return self.properties.get("hardwareHashExtractionEnabled", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def locale(self) -> Optional[str]:
        """Gets the locale property"""
        return self.properties.get("locale", None)

    @property
    def management_service_app_id(self) -> Optional[str]:
        """Gets the managementServiceAppId property"""
        return self.properties.get("managementServiceAppId", None)

    @property
    def out_of_box_experience_setting(self) -> OutOfBoxExperienceSetting:
        """Gets the outOfBoxExperienceSetting property"""
        from office365.intune.devices.configurations.windows.out_of_box_experience_setting import (
            OutOfBoxExperienceSetting,
        )

        return self.properties.get("outOfBoxExperienceSetting", OutOfBoxExperienceSetting())

    @property
    def preprovisioning_allowed(self) -> Optional[bool]:
        """Gets the preprovisioningAllowed property"""
        return self.properties.get("preprovisioningAllowed", None)

    @property
    def role_scope_tag_ids(self) -> StringCollection:
        """Gets the roleScopeTagIds property"""
        return self.properties.get("roleScopeTagIds", StringCollection())

    @property
    def assigned_devices(self) -> EntityCollection[WindowsAutopilotDeviceIdentity]:
        """Gets the assignedDevices property"""
        from office365.intune.devices.management.windows_autopilot_device_identity import (
            WindowsAutopilotDeviceIdentity,
        )

        return self.properties.get(
            "assignedDevices",
            EntityCollection[WindowsAutopilotDeviceIdentity](
                self.context, WindowsAutopilotDeviceIdentity, ResourcePath("assignedDevices", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsAutopilotDeploymentProfile"
