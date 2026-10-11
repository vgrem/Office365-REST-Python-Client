from __future__ import annotations

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.ediscovery.review_set_query import EdiscoveryReviewSetQuery


class EdiscoveryReviewSet(Entity):
    @property
    def queries(self) -> EntityCollection[EdiscoveryReviewSetQuery]:
        """Gets the queries property"""
        return self.properties.get(
            "queries",
            EntityCollection[EdiscoveryReviewSetQuery](
                self.context, EdiscoveryReviewSetQuery, ResourcePath("queries", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.EdiscoveryReviewSet"
