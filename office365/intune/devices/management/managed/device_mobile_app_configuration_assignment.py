from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.policies.conditionalaccess.device_and_app_management_assignment_target import (
        DeviceAndAppManagementAssignmentTarget,
    )


class ManagedDeviceMobileAppConfigurationAssignment(Entity):
    @property
    def target(self) -> DeviceAndAppManagementAssignmentTarget:
        """Gets the target property"""
        from office365.directory.policies.conditionalaccess.device_and_app_management_assignment_target import (
            DeviceAndAppManagementAssignmentTarget,
        )

        return self.properties.get("target", DeviceAndAppManagementAssignmentTarget())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ManagedDeviceMobileAppConfigurationAssignment"
