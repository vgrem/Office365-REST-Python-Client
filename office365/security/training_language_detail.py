from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.permissions.email_identity import EmailIdentity


class TrainingLanguageDetail(Entity):
    @property
    def content(self) -> Optional[str]:
        """Gets the content property"""
        return self.properties.get("content", None)

    @property
    def created_by(self) -> EmailIdentity:
        """Gets the createdBy property"""
        from office365.directory.permissions.email_identity import EmailIdentity

        return self.properties.get("createdBy", EmailIdentity())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def is_default_langauge(self) -> Optional[bool]:
        """Gets the isDefaultLangauge property"""
        return self.properties.get("isDefaultLangauge", None)

    @property
    def last_modified_by(self) -> EmailIdentity:
        """Gets the lastModifiedBy property"""
        from office365.directory.permissions.email_identity import EmailIdentity

        return self.properties.get("lastModifiedBy", EmailIdentity())

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def locale(self) -> Optional[str]:
        """Gets the locale property"""
        return self.properties.get("locale", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TrainingLanguageDetail"
