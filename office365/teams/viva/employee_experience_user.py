from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.viva.learning.courses.activity import LearningCourseActivity

if TYPE_CHECKING:
    from office365.common.engagement_role import EngagementRole


class EmployeeExperienceUser(Entity):
    """"""

    @property
    def learning_course_activities(self) -> EntityCollection[LearningCourseActivity]:
        """Get a list of the learningCourseActivity objects (assigned or self-initiated) for a user."""
        return self.properties.get(
            "learningCourseActivities",
            EntityCollection(
                self.context, LearningCourseActivity, ResourcePath("learningCourseActivities", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EmployeeExperienceUser"

    @property
    def assigned_roles(self) -> EntityCollection[EngagementRole]:
        """Gets the assignedRoles property"""
        from office365.common.engagement_role import EngagementRole

        return self.properties.get(
            "assignedRoles",
            EntityCollection[EngagementRole](
                self.context, EngagementRole, ResourcePath("assignedRoles", self.resource_path)
            ),
        )
