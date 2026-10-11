from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.unified_role_eligibility_schedule_instance import (
        UnifiedRoleEligibilityScheduleInstance,
    )


class UnifiedRoleAssignmentScheduleInstance(Entity):
    @property
    def assignment_type(self) -> Optional[str]:
        """Gets the assignmentType property"""
        return self.properties.get("assignmentType", None)

    @property
    def end_date_time(self) -> Optional[datetime]:
        """Gets the endDateTime property"""
        return self.properties.get("endDateTime", datetime.min)

    @property
    def member_type(self) -> Optional[str]:
        """Gets the memberType property"""
        return self.properties.get("memberType", None)

    @property
    def role_assignment_origin_id(self) -> Optional[str]:
        """Gets the roleAssignmentOriginId property"""
        return self.properties.get("roleAssignmentOriginId", None)

    @property
    def role_assignment_schedule_id(self) -> Optional[str]:
        """Gets the roleAssignmentScheduleId property"""
        return self.properties.get("roleAssignmentScheduleId", None)

    @property
    def start_date_time(self) -> Optional[datetime]:
        """Gets the startDateTime property"""
        return self.properties.get("startDateTime", datetime.min)

    @property
    def activated_using(self) -> UnifiedRoleEligibilityScheduleInstance:
        """Gets the activatedUsing property"""
        from office365.directory.unified_role_eligibility_schedule_instance import (
            UnifiedRoleEligibilityScheduleInstance,
        )

        return self.properties.get(
            "activatedUsing",
            UnifiedRoleEligibilityScheduleInstance(self.context, ResourcePath("activatedUsing", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleAssignmentScheduleInstance"
