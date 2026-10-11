from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.runtime.types.duration import timedelta
    from office365.teams.viva.learning.level import Level


class LearningContent(Entity):
    """Represents the metadata of content for employee learning."""

    @property
    def additional_tags(self) -> StringCollection:
        """Gets the additionalTags property"""
        return self.properties.get("additionalTags", StringCollection())

    @property
    def content_web_url(self) -> Optional[str]:
        """Gets the contentWebUrl property"""
        return self.properties.get("contentWebUrl", None)

    @property
    def contributors(self) -> StringCollection:
        """Gets the contributors property"""
        return self.properties.get("contributors", StringCollection())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def duration(self) -> Optional[timedelta]:
        """Gets the duration property"""
        return self.properties.get("duration", None)

    @property
    def external_id(self) -> Optional[str]:
        """Gets the externalId property"""
        return self.properties.get("externalId", None)

    @property
    def format(self) -> Optional[str]:
        """Gets the format property"""
        return self.properties.get("format", None)

    @property
    def is_active(self) -> Optional[bool]:
        """Gets the isActive property"""
        return self.properties.get("isActive", None)

    @property
    def is_premium(self) -> Optional[bool]:
        """Gets the isPremium property"""
        return self.properties.get("isPremium", None)

    @property
    def is_searchable(self) -> Optional[bool]:
        """Gets the isSearchable property"""
        return self.properties.get("isSearchable", None)

    @property
    def language_tag(self) -> Optional[str]:
        """Gets the languageTag property"""
        return self.properties.get("languageTag", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def level(self) -> Level:
        """Gets the level property"""
        from office365.teams.viva.learning.level import Level

        return self.properties.get("level", Level.beginner)

    @property
    def number_of_pages(self) -> Optional[int]:
        """Gets the numberOfPages property"""
        return self.properties.get("numberOfPages", None)

    @property
    def skill_tags(self) -> StringCollection:
        """Gets the skillTags property"""
        return self.properties.get("skillTags", StringCollection())

    @property
    def source_name(self) -> Optional[str]:
        """Gets the sourceName property"""
        return self.properties.get("sourceName", None)

    @property
    def thumbnail_web_url(self) -> Optional[str]:
        """Gets the thumbnailWebUrl property"""
        return self.properties.get("thumbnailWebUrl", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the title property"""
        return self.properties.get("title", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.LearningContent"
