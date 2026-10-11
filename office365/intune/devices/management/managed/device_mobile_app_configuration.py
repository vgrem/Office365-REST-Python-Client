from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.intune.devices.management.managed.device_mobile_app_configuration_assignment import (
        ManagedDeviceMobileAppConfigurationAssignment,
    )
    from office365.intune.devices.management.managed.device_mobile_app_configuration_device_status import (
        ManagedDeviceMobileAppConfigurationDeviceStatus,
    )
    from office365.intune.devices.management.managed.device_mobile_app_configuration_device_summary import (
        ManagedDeviceMobileAppConfigurationDeviceSummary,
    )
    from office365.intune.devices.management.managed.device_mobile_app_configuration_user_status import (
        ManagedDeviceMobileAppConfigurationUserStatus,
    )
    from office365.intune.devices.management.managed.device_mobile_app_configuration_user_summary import (
        ManagedDeviceMobileAppConfigurationUserSummary,
    )


class ManagedDeviceMobileAppConfiguration(Entity):
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
    def targeted_mobile_apps(self) -> StringCollection:
        """Gets the targetedMobileApps property"""
        return self.properties.get("targetedMobileApps", StringCollection())

    @property
    def version(self) -> Optional[int]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def assignments(self) -> EntityCollection[ManagedDeviceMobileAppConfigurationAssignment]:
        """Gets the assignments property"""
        from office365.intune.devices.management.managed.device_mobile_app_configuration_assignment import (
            ManagedDeviceMobileAppConfigurationAssignment,
        )

        return self.properties.get(
            "assignments",
            EntityCollection[ManagedDeviceMobileAppConfigurationAssignment](
                self.context,
                ManagedDeviceMobileAppConfigurationAssignment,
                ResourcePath("assignments", self.resource_path),
            ),
        )

    @property
    def device_statuses(self) -> EntityCollection[ManagedDeviceMobileAppConfigurationDeviceStatus]:
        """Gets the deviceStatuses property"""
        from office365.intune.devices.management.managed.device_mobile_app_configuration_device_status import (
            ManagedDeviceMobileAppConfigurationDeviceStatus,
        )

        return self.properties.get(
            "deviceStatuses",
            EntityCollection[ManagedDeviceMobileAppConfigurationDeviceStatus](
                self.context,
                ManagedDeviceMobileAppConfigurationDeviceStatus,
                ResourcePath("deviceStatuses", self.resource_path),
            ),
        )

    @property
    def device_status_summary(self) -> ManagedDeviceMobileAppConfigurationDeviceSummary:
        """Gets the deviceStatusSummary property"""
        from office365.intune.devices.management.managed.device_mobile_app_configuration_device_summary import (
            ManagedDeviceMobileAppConfigurationDeviceSummary,
        )

        return self.properties.get(
            "deviceStatusSummary",
            ManagedDeviceMobileAppConfigurationDeviceSummary(
                self.context, ResourcePath("deviceStatusSummary", self.resource_path)
            ),
        )

    @property
    def user_statuses(self) -> EntityCollection[ManagedDeviceMobileAppConfigurationUserStatus]:
        """Gets the userStatuses property"""
        from office365.intune.devices.management.managed.device_mobile_app_configuration_user_status import (
            ManagedDeviceMobileAppConfigurationUserStatus,
        )

        return self.properties.get(
            "userStatuses",
            EntityCollection[ManagedDeviceMobileAppConfigurationUserStatus](
                self.context,
                ManagedDeviceMobileAppConfigurationUserStatus,
                ResourcePath("userStatuses", self.resource_path),
            ),
        )

    @property
    def user_status_summary(self) -> ManagedDeviceMobileAppConfigurationUserSummary:
        """Gets the userStatusSummary property"""
        from office365.intune.devices.management.managed.device_mobile_app_configuration_user_summary import (
            ManagedDeviceMobileAppConfigurationUserSummary,
        )

        return self.properties.get(
            "userStatusSummary",
            ManagedDeviceMobileAppConfigurationUserSummary(
                self.context, ResourcePath("userStatusSummary", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ManagedDeviceMobileAppConfiguration"
