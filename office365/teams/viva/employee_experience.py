from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.teams.viva.community import Community
from office365.teams.viva.learning.courses.activity import LearningCourseActivity
from office365.teams.viva.learning.provider import LearningProvider

if TYPE_CHECKING:
    from office365.common.engagement_async_operation import EngagementAsyncOperation
    from office365.common.engagement_role import EngagementRole


class EmployeeExperience(Entity):
    """Represents a container that exposes navigation properties for employee experience resources."""

    @property
    def communities(self) -> EntityCollection[Community]:
        """A collection of communities in Viva Engage."""
        return self.properties.get(
            "communities",
            EntityCollection(
                self.context,
                Community,
                ResourcePath("communities", self.resource_path),
            ),
        )

    @odata(name="learningCourseActivities")
    @property
    def learning_course_activities(self) -> EntityCollection[LearningCourseActivity]:
        """A collection of learning course activities."""
        return self.properties.get(
            "learningCourseActivities",
            EntityCollection(
                self.context,
                LearningCourseActivity,
                ResourcePath("learningCourseActivities", self.resource_path),
            ),
        )

    @odata(name="learningProviders")
    @property
    def learning_providers(self) -> EntityCollection[LearningProvider]:
        """A collection of learning providers."""
        return self.properties.get(
            "learningProviders",
            EntityCollection(
                self.context,
                LearningProvider,
                ResourcePath("learningProviders", self.resource_path),
            ),
        )

    @property
    def engagement_async_operations(self) -> EntityCollection[EngagementAsyncOperation]:
        """Gets the engagementAsyncOperations property"""
        from office365.common.engagement_async_operation import EngagementAsyncOperation

        return self.properties.get(
            "engagementAsyncOperations",
            EntityCollection[EngagementAsyncOperation](
                self.context, EngagementAsyncOperation, ResourcePath("engagementAsyncOperations", self.resource_path)
            ),
        )

    @property
    def roles(self) -> EntityCollection[EngagementRole]:
        """Gets the roles property"""
        from office365.common.engagement_role import EngagementRole

        return self.properties.get(
            "roles",
            EntityCollection[EngagementRole](self.context, EngagementRole, ResourcePath("roles", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EmployeeExperience"
