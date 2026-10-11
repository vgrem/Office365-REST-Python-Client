from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.intune.policies.installintent import InstallIntent

if TYPE_CHECKING:
    from office365.directory.policies.conditionalaccess.device_and_app_management_assignment_target import (
        DeviceAndAppManagementAssignmentTarget,
    )
    from office365.intune.devices.management.mobileapps.mobile_app_assignment_settings import (
        MobileAppAssignmentSettings,
    )


class MobileAppAssignment(Entity):
    @property
    def intent(self) -> InstallIntent:
        """Gets the intent property"""
        return self.properties.get("intent", InstallIntent.available)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MobileAppAssignment"

    @property
    def settings(self) -> MobileAppAssignmentSettings:
        """Gets the settings property"""
        from office365.intune.devices.management.mobileapps.mobile_app_assignment_settings import (
            MobileAppAssignmentSettings,
        )

        return self.properties.get("settings", MobileAppAssignmentSettings())

    @property
    def target(self) -> DeviceAndAppManagementAssignmentTarget:
        """Gets the target property"""
        from office365.directory.policies.conditionalaccess.device_and_app_management_assignment_target import (
            DeviceAndAppManagementAssignmentTarget,
        )

        return self.properties.get("target", DeviceAndAppManagementAssignmentTarget())
