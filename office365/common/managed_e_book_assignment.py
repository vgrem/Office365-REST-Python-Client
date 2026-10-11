from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.policies.conditionalaccess.device_and_app_management_assignment_target import (
        DeviceAndAppManagementAssignmentTarget,
    )
    from office365.intune.policies.installintent import InstallIntent


class ManagedEBookAssignment(Entity):
    @property
    def install_intent(self) -> InstallIntent:
        """Gets the installIntent property"""
        from office365.intune.policies.installintent import InstallIntent

        return self.properties.get("installIntent", InstallIntent.available)

    @property
    def target(self) -> DeviceAndAppManagementAssignmentTarget:
        """Gets the target property"""
        from office365.directory.policies.conditionalaccess.device_and_app_management_assignment_target import (
            DeviceAndAppManagementAssignmentTarget,
        )

        return self.properties.get("target", DeviceAndAppManagementAssignmentTarget())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ManagedEBookAssignment"
