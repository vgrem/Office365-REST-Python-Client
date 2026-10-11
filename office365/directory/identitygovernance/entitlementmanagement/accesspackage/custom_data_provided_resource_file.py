from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity


class CustomDataProvidedResourceFile(Entity):
    @property
    def name(self) -> Optional[str]:
        """Gets the name property"""
        return self.properties.get("name", None)

    @property
    def size(self) -> Optional[int]:
        """Gets the size property"""
        return self.properties.get("size", None)

    @property
    def uploaded_date_time(self) -> Optional[datetime]:
        """Gets the uploadedDateTime property"""
        return self.properties.get("uploadedDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CustomDataProvidedResourceFile"
