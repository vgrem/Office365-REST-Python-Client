from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.content_activity import ContentActivity


class ActivitiesContainer(Entity):
    @property
    def content_activities(self) -> EntityCollection[ContentActivity]:
        """Gets the contentActivities property"""
        from office365.directory.identitygovernance.content_activity import (
            ContentActivity,
        )

        return self.properties.get(
            "contentActivities",
            EntityCollection[ContentActivity](
                self.context, ContentActivity, ResourcePath("contentActivities", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ActivitiesContainer"
