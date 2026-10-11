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
    from office365.intune.devices.compliance_device_overview import (
        DeviceComplianceDeviceOverview,
    )
    from office365.intune.devices.compliance_device_status import (
        DeviceComplianceDeviceStatus,
    )
    from office365.intune.devices.compliance_policy_assignment import (
        DeviceCompliancePolicyAssignment,
    )
    from office365.intune.devices.compliance_scheduled_action_for_rule import (
        DeviceComplianceScheduledActionForRule,
    )
    from office365.intune.devices.compliance_user_overview import (
        DeviceComplianceUserOverview,
    )
    from office365.intune.devices.compliance_user_status import (
        DeviceComplianceUserStatus,
    )


class DeviceCompliancePolicy(Entity):
    """This is the base class for Compliance policy. Compliance policies are platform specific and individual
    per-platform compliance policies inherit from here"""

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
    def assignments(self) -> EntityCollection[DeviceCompliancePolicyAssignment]:
        """Gets the assignments property"""
        from office365.intune.devices.compliance_policy_assignment import (
            DeviceCompliancePolicyAssignment,
        )

        return self.properties.get(
            "assignments",
            EntityCollection[DeviceCompliancePolicyAssignment](
                self.context, DeviceCompliancePolicyAssignment, ResourcePath("assignments", self.resource_path)
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
    def device_statuses(self) -> EntityCollection[DeviceComplianceDeviceStatus]:
        """Gets the deviceStatuses property"""
        from office365.intune.devices.compliance_device_status import (
            DeviceComplianceDeviceStatus,
        )

        return self.properties.get(
            "deviceStatuses",
            EntityCollection[DeviceComplianceDeviceStatus](
                self.context, DeviceComplianceDeviceStatus, ResourcePath("deviceStatuses", self.resource_path)
            ),
        )

    @property
    def device_status_overview(self) -> DeviceComplianceDeviceOverview:
        """Gets the deviceStatusOverview property"""
        from office365.intune.devices.compliance_device_overview import (
            DeviceComplianceDeviceOverview,
        )

        return self.properties.get(
            "deviceStatusOverview",
            DeviceComplianceDeviceOverview(self.context, ResourcePath("deviceStatusOverview", self.resource_path)),
        )

    @property
    def scheduled_actions_for_rule(self) -> EntityCollection[DeviceComplianceScheduledActionForRule]:
        """Gets the scheduledActionsForRule property"""
        from office365.intune.devices.compliance_scheduled_action_for_rule import (
            DeviceComplianceScheduledActionForRule,
        )

        return self.properties.get(
            "scheduledActionsForRule",
            EntityCollection[DeviceComplianceScheduledActionForRule](
                self.context,
                DeviceComplianceScheduledActionForRule,
                ResourcePath("scheduledActionsForRule", self.resource_path),
            ),
        )

    @property
    def user_statuses(self) -> EntityCollection[DeviceComplianceUserStatus]:
        """Gets the userStatuses property"""
        from office365.intune.devices.compliance_user_status import (
            DeviceComplianceUserStatus,
        )

        return self.properties.get(
            "userStatuses",
            EntityCollection[DeviceComplianceUserStatus](
                self.context, DeviceComplianceUserStatus, ResourcePath("userStatuses", self.resource_path)
            ),
        )

    @property
    def user_status_overview(self) -> DeviceComplianceUserOverview:
        """Gets the userStatusOverview property"""
        from office365.intune.devices.compliance_user_overview import (
            DeviceComplianceUserOverview,
        )

        return self.properties.get(
            "userStatusOverview",
            DeviceComplianceUserOverview(self.context, ResourcePath("userStatusOverview", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceCompliancePolicy"
