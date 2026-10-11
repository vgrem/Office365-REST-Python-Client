from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.users.user import User
    from office365.intune.devices.management.virtualendpoint.cloudpcs.managementassignmenttarget import (
        CloudPcManagementAssignmentTarget,
    )


class CloudPcProvisioningPolicyAssignment(Entity):
    @property
    def target(self) -> CloudPcManagementAssignmentTarget:
        """Gets the target property"""
        from office365.intune.devices.management.virtualendpoint.cloudpcs.managementassignmenttarget import (
            CloudPcManagementAssignmentTarget,
        )

        return self.properties.get("target", CloudPcManagementAssignmentTarget())

    @property
    def assigned_users(self) -> EntityCollection[User]:
        """Gets the assignedUsers property"""
        from office365.directory.users.user import User

        return self.properties.get(
            "assignedUsers",
            EntityCollection[User](self.context, User, ResourcePath("assignedUsers", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CloudPcProvisioningPolicyAssignment"
