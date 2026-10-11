from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.security.subcategory_template import SubcategoryTemplate


class CategoryTemplate(Entity):
    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.CategoryTemplate"

    @property
    def subcategories(self) -> EntityCollection[SubcategoryTemplate]:
        """Gets the subcategories property"""
        from office365.security.subcategory_template import (
            SubcategoryTemplate,
        )

        return self.properties.get(
            "subcategories",
            EntityCollection[SubcategoryTemplate](
                self.context, SubcategoryTemplate, ResourcePath("subcategories", self.resource_path)
            ),
        )
