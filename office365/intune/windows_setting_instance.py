from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity


class WindowsSettingInstance(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def expiration_date_time(self) -> Optional[datetime]:
        """Gets the expirationDateTime property"""
        return self.properties.get("expirationDateTime", datetime.min)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def payload(self) -> Optional[str]:
        """Gets the payload property"""
        return self.properties.get("payload", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsSettingInstance"
