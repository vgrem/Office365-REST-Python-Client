from __future__ import annotations

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.childselectability import ChildSelectability


class EdiscoveryReviewTag(Entity):
    @property
    def child_selectability(self) -> ChildSelectability:
        """Gets the childSelectability property"""
        return self.properties.get("childSelectability", ChildSelectability.One)

    @property
    def child_tags(self) -> EntityCollection[EdiscoveryReviewTag]:
        """Gets the childTags property"""
        return self.properties.get(
            "childTags",
            EntityCollection[EdiscoveryReviewTag](
                self.context, EdiscoveryReviewTag, ResourcePath("childTags", self.resource_path)
            ),
        )

    @property
    def parent(self) -> EdiscoveryReviewTag:
        """Gets the parent property"""
        return self.properties.get(
            "parent", EdiscoveryReviewTag(self.context, ResourcePath("parent", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.EdiscoveryReviewTag"
