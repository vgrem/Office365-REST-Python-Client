from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.objects.object import DirectoryObject
    from office365.directory.policies.unifiedrolemanagement.unifiedroleschedulerequestactions import (
        UnifiedRoleScheduleRequestActions,
    )
    from office365.directory.request_schedule import RequestSchedule
    from office365.directory.rolemanagement.app_scope import AppScope
    from office365.directory.rolemanagement.unifiedrole.definition import (
        UnifiedRoleDefinition,
    )
    from office365.directory.ticket_info import TicketInfo
    from office365.directory.unified_role_assignment_schedule import (
        UnifiedRoleAssignmentSchedule,
    )
    from office365.directory.unified_role_eligibility_schedule import (
        UnifiedRoleEligibilitySchedule,
    )


class UnifiedRoleAssignmentScheduleRequest(Entity):
    """In PIM, represents a request for an active role assignment to a principal. The role assignment can be
    permanently active with or without an expiry date, or temporarily active after activation of an eligible
    assignment. Inherits from request."""

    @property
    def action(self) -> UnifiedRoleScheduleRequestActions:
        """Gets the action property"""
        from office365.directory.policies.unifiedrolemanagement.unifiedroleschedulerequestactions import (
            UnifiedRoleScheduleRequestActions,
        )

        return self.properties.get("action", UnifiedRoleScheduleRequestActions.adminAssign)

    @property
    def app_scope_id(self) -> Optional[str]:
        """Gets the appScopeId property"""
        return self.properties.get("appScopeId", None)

    @property
    def directory_scope_id(self) -> Optional[str]:
        """Gets the directoryScopeId property"""
        return self.properties.get("directoryScopeId", None)

    @property
    def is_validation_only(self) -> Optional[bool]:
        """Gets the isValidationOnly property"""
        return self.properties.get("isValidationOnly", None)

    @property
    def justification(self) -> Optional[str]:
        """Gets the justification property"""
        return self.properties.get("justification", None)

    @property
    def principal_id(self) -> Optional[str]:
        """Gets the principalId property"""
        return self.properties.get("principalId", None)

    @property
    def role_definition_id(self) -> Optional[str]:
        """Gets the roleDefinitionId property"""
        return self.properties.get("roleDefinitionId", None)

    @property
    def schedule_info(self) -> RequestSchedule:
        """Gets the scheduleInfo property"""
        from office365.directory.request_schedule import RequestSchedule

        return self.properties.get("scheduleInfo", RequestSchedule())

    @property
    def target_schedule_id(self) -> Optional[str]:
        """Gets the targetScheduleId property"""
        return self.properties.get("targetScheduleId", None)

    @property
    def ticket_info(self) -> TicketInfo:
        """Gets the ticketInfo property"""
        from office365.directory.ticket_info import TicketInfo

        return self.properties.get("ticketInfo", TicketInfo())

    @property
    def activated_using(self) -> UnifiedRoleEligibilitySchedule:
        """Gets the activatedUsing property"""
        from office365.directory.unified_role_eligibility_schedule import (
            UnifiedRoleEligibilitySchedule,
        )

        return self.properties.get(
            "activatedUsing",
            UnifiedRoleEligibilitySchedule(self.context, ResourcePath("activatedUsing", self.resource_path)),
        )

    @property
    def app_scope(self) -> AppScope:
        """Gets the appScope property"""
        from office365.directory.rolemanagement.app_scope import AppScope

        return self.properties.get("appScope", AppScope(self.context, ResourcePath("appScope", self.resource_path)))

    @property
    def directory_scope(self) -> DirectoryObject:
        """Gets the directoryScope property"""
        from office365.directory.objects.object import DirectoryObject

        return self.properties.get(
            "directoryScope", DirectoryObject(self.context, ResourcePath("directoryScope", self.resource_path))
        )

    @property
    def principal(self) -> DirectoryObject:
        """Gets the principal property"""
        from office365.directory.objects.object import DirectoryObject

        return self.properties.get(
            "principal", DirectoryObject(self.context, ResourcePath("principal", self.resource_path))
        )

    @property
    def role_definition(self) -> UnifiedRoleDefinition:
        """Gets the roleDefinition property"""
        from office365.directory.rolemanagement.unifiedrole.definition import (
            UnifiedRoleDefinition,
        )

        return self.properties.get(
            "roleDefinition", UnifiedRoleDefinition(self.context, ResourcePath("roleDefinition", self.resource_path))
        )

    @property
    def target_schedule(self) -> UnifiedRoleAssignmentSchedule:
        """Gets the targetSchedule property"""
        from office365.directory.unified_role_assignment_schedule import (
            UnifiedRoleAssignmentSchedule,
        )

        return self.properties.get(
            "targetSchedule",
            UnifiedRoleAssignmentSchedule(self.context, ResourcePath("targetSchedule", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleAssignmentScheduleRequest"
