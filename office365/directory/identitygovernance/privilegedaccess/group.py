from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.identitygovernance.privilegedaccess.approval import Approval
from office365.directory.identitygovernance.privilegedaccess.group_assignment_schedule import (
    PrivilegedAccessGroupAssignmentSchedule,
)
from office365.directory.identitygovernance.privilegedaccess.group_assignment_schedule_request import (
    PrivilegedAccessGroupAssignmentScheduleRequest,
)
from office365.directory.identitygovernance.privilegedaccess.group_eligibility_schedule import (
    PrivilegedAccessGroupEligibilitySchedule,
)
from office365.directory.identitygovernance.privilegedaccess.group_eligibility_schedule_instance import (
    PrivilegedAccessGroupEligibilityScheduleInstance,
)
from office365.directory.identitygovernance.privilegedaccess.group_eligibility_schedule_request import (
    PrivilegedAccessGroupEligibilityScheduleRequest,
)
from office365.directory.identitygovernance.privilegedaccess.schedule.group_assignment_instance import (
    PrivilegedAccessGroupAssignmentScheduleInstance,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.privilegedaccess.group_resource import (
        GroupResource,
    )


class PrivilegedAccessGroup(Entity):
    """The entry point for all resources related to Privileged Identity Management (PIM) for groups."""

    @property
    def assignment_approvals(self):
        """ """
        return self.properties.get(
            "assignmentApprovals",
            EntityCollection(self.context, Approval, ResourcePath("assignmentApprovals", self.resource_path)),
        )

    @property
    def assignment_schedule_instances(self):
        """The instances of assignment schedules to activate a just-in-time access."""
        return self.properties.get(
            "assignmentScheduleInstances",
            EntityCollection(
                self.context,
                PrivilegedAccessGroupAssignmentScheduleInstance,
                ResourcePath("assignmentScheduleInstances", self.resource_path),
            ),
        )

    @property
    def assignment_schedule_requests(self) -> EntityCollection[PrivilegedAccessGroupAssignmentScheduleRequest]:
        """Gets the assignmentScheduleRequests property"""
        return self.properties.get(
            "assignmentScheduleRequests",
            EntityCollection[PrivilegedAccessGroupAssignmentScheduleRequest](
                self.context,
                PrivilegedAccessGroupAssignmentScheduleRequest,
                ResourcePath("assignmentScheduleRequests", self.resource_path),
            ),
        )

    @property
    def assignment_schedules(self) -> EntityCollection[PrivilegedAccessGroupAssignmentSchedule]:
        """Gets the assignmentSchedules property"""
        return self.properties.get(
            "assignmentSchedules",
            EntityCollection[PrivilegedAccessGroupAssignmentSchedule](
                self.context,
                PrivilegedAccessGroupAssignmentSchedule,
                ResourcePath("assignmentSchedules", self.resource_path),
            ),
        )

    @property
    def eligibility_schedule_instances(self) -> EntityCollection[PrivilegedAccessGroupEligibilityScheduleInstance]:
        """Gets the eligibilityScheduleInstances property"""
        return self.properties.get(
            "eligibilityScheduleInstances",
            EntityCollection[PrivilegedAccessGroupEligibilityScheduleInstance](
                self.context,
                PrivilegedAccessGroupEligibilityScheduleInstance,
                ResourcePath("eligibilityScheduleInstances", self.resource_path),
            ),
        )

    @property
    def eligibility_schedule_requests(self) -> EntityCollection[PrivilegedAccessGroupEligibilityScheduleRequest]:
        """Gets the eligibilityScheduleRequests property"""
        return self.properties.get(
            "eligibilityScheduleRequests",
            EntityCollection[PrivilegedAccessGroupEligibilityScheduleRequest](
                self.context,
                PrivilegedAccessGroupEligibilityScheduleRequest,
                ResourcePath("eligibilityScheduleRequests", self.resource_path),
            ),
        )

    @property
    def eligibility_schedules(self) -> EntityCollection[PrivilegedAccessGroupEligibilitySchedule]:
        """Gets the eligibilitySchedules property"""
        return self.properties.get(
            "eligibilitySchedules",
            EntityCollection[PrivilegedAccessGroupEligibilitySchedule](
                self.context,
                PrivilegedAccessGroupEligibilitySchedule,
                ResourcePath("eligibilitySchedules", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrivilegedAccessGroup"

    @property
    def resources(self) -> EntityCollection[GroupResource]:
        """Gets the resources property"""
        from office365.directory.identitygovernance.privilegedaccess.group_resource import (
            GroupResource,
        )

        return self.properties.get(
            "resources",
            EntityCollection[GroupResource](self.context, GroupResource, ResourcePath("resources", self.resource_path)),
        )
