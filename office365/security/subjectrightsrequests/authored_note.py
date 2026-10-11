from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.permissions.identity import Identity
    from office365.outlook.mail.item_body import ItemBody


class AuthoredNote(Entity):
    @property
    def author(self) -> Identity:
        """Gets the author property"""
        from office365.directory.permissions.identity import Identity

        return self.properties.get("author", Identity())

    @property
    def content(self) -> ItemBody:
        """Gets the content property"""
        from office365.outlook.mail.item_body import ItemBody

        return self.properties.get("content", ItemBody())

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AuthoredNote"
