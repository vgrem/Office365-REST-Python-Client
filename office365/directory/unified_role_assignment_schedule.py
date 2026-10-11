from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.request_schedule import RequestSchedule
    from office365.directory.unified_role_eligibility_schedule import (
        UnifiedRoleEligibilitySchedule,
    )


class UnifiedRoleAssignmentSchedule(Entity):
    @property
    def assignment_type(self) -> Optional[str]:
        """Gets the assignmentType property"""
        return self.properties.get("assignmentType", None)

    @property
    def member_type(self) -> Optional[str]:
        """Gets the memberType property"""
        return self.properties.get("memberType", None)

    @property
    def schedule_info(self) -> RequestSchedule:
        """Gets the scheduleInfo property"""
        from office365.directory.request_schedule import RequestSchedule

        return self.properties.get("scheduleInfo", RequestSchedule())

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
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleAssignmentSchedule"
