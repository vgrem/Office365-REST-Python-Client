from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity


class LocalizedNotificationMessage(Entity):
    @property
    def is_default(self) -> Optional[bool]:
        """Gets the isDefault property"""
        return self.properties.get("isDefault", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def locale(self) -> Optional[str]:
        """Gets the locale property"""
        return self.properties.get("locale", None)

    @property
    def message_template(self) -> Optional[str]:
        """Gets the messageTemplate property"""
        return self.properties.get("messageTemplate", None)

    @property
    def subject(self) -> Optional[str]:
        """Gets the subject property"""
        return self.properties.get("subject", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.LocalizedNotificationMessage"
