from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.policies.unifiedrolemanagement.unified_role_assignment_schedule_request import (
    UnifiedRoleAssignmentScheduleRequest,
)
from office365.directory.rolemanagement.unifiedrole.assignment import (
    UnifiedRoleAssignment,
)
from office365.directory.rolemanagement.unifiedrole.definition import (
    UnifiedRoleDefinition,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.directory.unified_rbac_resource_namespace import (
        UnifiedRbacResourceNamespace,
    )
    from office365.directory.unified_role_assignment_schedule import (
        UnifiedRoleAssignmentSchedule,
    )
    from office365.directory.unified_role_assignment_schedule_instance import (
        UnifiedRoleAssignmentScheduleInstance,
    )
    from office365.directory.unified_role_eligibility_schedule import (
        UnifiedRoleEligibilitySchedule,
    )
    from office365.directory.unified_role_eligibility_schedule_instance import (
        UnifiedRoleEligibilityScheduleInstance,
    )
    from office365.directory.unified_role_eligibility_schedule_request import (
        UnifiedRoleEligibilityScheduleRequest,
    )


class RbacApplication(Entity):
    """Role management container for unified role definitions and role assignments for Microsoft 365 role-based
    access control (RBAC) providers. The role assignments support only a single principal and a single scope.
    Currently directory and entitlementManagement are the two RBAC providers supported.
    """

    @odata(name="roleAssignments")
    @property
    def role_assignments(self) -> EntityCollection[UnifiedRoleAssignment]:
        """Resource to grant access to users or groups."""
        return self.properties.get(
            "roleAssignments",
            EntityCollection(
                self.context,
                UnifiedRoleAssignment,
                ResourcePath("roleAssignments", self.resource_path),
            ),
        )

    @odata(name="roleDefinitions")
    @property
    def role_definitions(self) -> EntityCollection[UnifiedRoleDefinition]:
        """Resource representing the roles allowed by RBAC providers and the permissions assigned to the roles."""
        return self.properties.get(
            "roleDefinitions",
            EntityCollection(
                self.context,
                UnifiedRoleDefinition,
                ResourcePath("roleDefinitions", self.resource_path),
            ),
        )

    @odata(name="roleAssignmentScheduleRequests")
    @property
    def role_assignment_schedule_requests(
        self,
    ) -> EntityCollection[UnifiedRoleAssignmentScheduleRequest]:
        """Resource representing the roles allowed by RBAC providers and the permissions assigned to the roles."""
        return self.properties.get(
            "roleAssignmentScheduleRequests",
            EntityCollection(
                self.context,
                UnifiedRoleAssignmentScheduleRequest,
                ResourcePath("roleAssignmentScheduleRequests", self.resource_path),
            ),
        )

    @property
    def resource_namespaces(self) -> EntityCollection[UnifiedRbacResourceNamespace]:
        """Gets the resourceNamespaces property"""
        from office365.directory.unified_rbac_resource_namespace import (
            UnifiedRbacResourceNamespace,
        )

        return self.properties.get(
            "resourceNamespaces",
            EntityCollection[UnifiedRbacResourceNamespace](
                self.context, UnifiedRbacResourceNamespace, ResourcePath("resourceNamespaces", self.resource_path)
            ),
        )

    @property
    def role_assignment_schedule_instances(self) -> EntityCollection[UnifiedRoleAssignmentScheduleInstance]:
        """Gets the roleAssignmentScheduleInstances property"""
        from office365.directory.unified_role_assignment_schedule_instance import (
            UnifiedRoleAssignmentScheduleInstance,
        )

        return self.properties.get(
            "roleAssignmentScheduleInstances",
            EntityCollection[UnifiedRoleAssignmentScheduleInstance](
                self.context,
                UnifiedRoleAssignmentScheduleInstance,
                ResourcePath("roleAssignmentScheduleInstances", self.resource_path),
            ),
        )

    @property
    def role_assignment_schedules(self) -> EntityCollection[UnifiedRoleAssignmentSchedule]:
        """Gets the roleAssignmentSchedules property"""
        from office365.directory.unified_role_assignment_schedule import (
            UnifiedRoleAssignmentSchedule,
        )

        return self.properties.get(
            "roleAssignmentSchedules",
            EntityCollection[UnifiedRoleAssignmentSchedule](
                self.context, UnifiedRoleAssignmentSchedule, ResourcePath("roleAssignmentSchedules", self.resource_path)
            ),
        )

    @property
    def role_eligibility_schedule_instances(self) -> EntityCollection[UnifiedRoleEligibilityScheduleInstance]:
        """Gets the roleEligibilityScheduleInstances property"""
        from office365.directory.unified_role_eligibility_schedule_instance import (
            UnifiedRoleEligibilityScheduleInstance,
        )

        return self.properties.get(
            "roleEligibilityScheduleInstances",
            EntityCollection[UnifiedRoleEligibilityScheduleInstance](
                self.context,
                UnifiedRoleEligibilityScheduleInstance,
                ResourcePath("roleEligibilityScheduleInstances", self.resource_path),
            ),
        )

    @property
    def role_eligibility_schedule_requests(self) -> EntityCollection[UnifiedRoleEligibilityScheduleRequest]:
        """Gets the roleEligibilityScheduleRequests property"""
        from office365.directory.unified_role_eligibility_schedule_request import (
            UnifiedRoleEligibilityScheduleRequest,
        )

        return self.properties.get(
            "roleEligibilityScheduleRequests",
            EntityCollection[UnifiedRoleEligibilityScheduleRequest](
                self.context,
                UnifiedRoleEligibilityScheduleRequest,
                ResourcePath("roleEligibilityScheduleRequests", self.resource_path),
            ),
        )

    @property
    def role_eligibility_schedules(self) -> EntityCollection[UnifiedRoleEligibilitySchedule]:
        """Gets the roleEligibilitySchedules property"""
        from office365.directory.unified_role_eligibility_schedule import (
            UnifiedRoleEligibilitySchedule,
        )

        return self.properties.get(
            "roleEligibilitySchedules",
            EntityCollection[UnifiedRoleEligibilitySchedule](
                self.context,
                UnifiedRoleEligibilitySchedule,
                ResourcePath("roleEligibilitySchedules", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RbacApplication"
