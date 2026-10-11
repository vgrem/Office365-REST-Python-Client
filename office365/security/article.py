from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.security.threatintelligence.article_indicator import (
    ArticleIndicator,
)

if TYPE_CHECKING:
    from office365.security.formatted_content import FormattedContent


class Article(Entity):
    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def image_url(self) -> Optional[str]:
        """Gets the imageUrl property"""
        return self.properties.get("imageUrl", None)

    @property
    def is_featured(self) -> Optional[bool]:
        """Gets the isFeatured property"""
        return self.properties.get("isFeatured", None)

    @property
    def last_updated_date_time(self) -> datetime:
        """Gets the lastUpdatedDateTime property"""
        return self.properties.get("lastUpdatedDateTime", datetime.min)

    @property
    def tags(self) -> StringCollection:
        """Gets the tags property"""
        return self.properties.get("tags", StringCollection(None))

    @property
    def title(self) -> Optional[str]:
        """Gets the title property"""
        return self.properties.get("title", None)

    @property
    def indicators(self) -> EntityCollection[ArticleIndicator]:
        """Gets the indicators property"""
        return self.properties.get(
            "indicators",
            EntityCollection[ArticleIndicator](
                self.context, ArticleIndicator, ResourcePath("indicators", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.Article"

    @property
    def body(self) -> FormattedContent:
        """Gets the body property"""
        from office365.security.formatted_content import FormattedContent

        return self.properties.get("body", FormattedContent())

    @property
    def summary(self) -> FormattedContent:
        """Gets the summary property"""
        from office365.security.formatted_content import FormattedContent

        return self.properties.get("summary", FormattedContent())
