from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.compliance.setting_state_device_summary import (
        SettingStateDeviceSummary,
    )
    from office365.intune.devices.configuration_assignment import (
        DeviceConfigurationAssignment,
    )
    from office365.intune.devices.configuration_device_overview import (
        DeviceConfigurationDeviceOverview,
    )
    from office365.intune.devices.configuration_device_status import (
        DeviceConfigurationDeviceStatus,
    )
    from office365.intune.devices.configuration_user_overview import (
        DeviceConfigurationUserOverview,
    )
    from office365.intune.devices.configuration_user_status import (
        DeviceConfigurationUserStatus,
    )


class DeviceConfiguration(Entity):
    """Device Configuration."""

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def version(self) -> Optional[int]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def assignments(self) -> EntityCollection[DeviceConfigurationAssignment]:
        """Gets the assignments property"""
        from office365.intune.devices.configuration_assignment import (
            DeviceConfigurationAssignment,
        )

        return self.properties.get(
            "assignments",
            EntityCollection[DeviceConfigurationAssignment](
                self.context, DeviceConfigurationAssignment, ResourcePath("assignments", self.resource_path)
            ),
        )

    @property
    def device_setting_state_summaries(self) -> EntityCollection[SettingStateDeviceSummary]:
        """Gets the deviceSettingStateSummaries property"""
        from office365.intune.devices.compliance.setting_state_device_summary import (
            SettingStateDeviceSummary,
        )

        return self.properties.get(
            "deviceSettingStateSummaries",
            EntityCollection[SettingStateDeviceSummary](
                self.context, SettingStateDeviceSummary, ResourcePath("deviceSettingStateSummaries", self.resource_path)
            ),
        )

    @property
    def device_statuses(self) -> EntityCollection[DeviceConfigurationDeviceStatus]:
        """Gets the deviceStatuses property"""
        from office365.intune.devices.configuration_device_status import (
            DeviceConfigurationDeviceStatus,
        )

        return self.properties.get(
            "deviceStatuses",
            EntityCollection[DeviceConfigurationDeviceStatus](
                self.context, DeviceConfigurationDeviceStatus, ResourcePath("deviceStatuses", self.resource_path)
            ),
        )

    @property
    def device_status_overview(self) -> DeviceConfigurationDeviceOverview:
        """Gets the deviceStatusOverview property"""
        from office365.intune.devices.configuration_device_overview import (
            DeviceConfigurationDeviceOverview,
        )

        return self.properties.get(
            "deviceStatusOverview",
            DeviceConfigurationDeviceOverview(self.context, ResourcePath("deviceStatusOverview", self.resource_path)),
        )

    @property
    def user_statuses(self) -> EntityCollection[DeviceConfigurationUserStatus]:
        """Gets the userStatuses property"""
        from office365.intune.devices.configuration_user_status import (
            DeviceConfigurationUserStatus,
        )

        return self.properties.get(
            "userStatuses",
            EntityCollection[DeviceConfigurationUserStatus](
                self.context, DeviceConfigurationUserStatus, ResourcePath("userStatuses", self.resource_path)
            ),
        )

    @property
    def user_status_overview(self) -> DeviceConfigurationUserOverview:
        """Gets the userStatusOverview property"""
        from office365.intune.devices.configuration_user_overview import (
            DeviceConfigurationUserOverview,
        )

        return self.properties.get(
            "userStatusOverview",
            DeviceConfigurationUserOverview(self.context, ResourcePath("userStatusOverview", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceConfiguration"
