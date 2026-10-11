from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity


class PrintDocument(Entity):
    @property
    def content_type(self) -> Optional[str]:
        """Gets the contentType property"""
        return self.properties.get("contentType", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def downloaded_date_time(self) -> Optional[datetime]:
        """Gets the downloadedDateTime property"""
        return self.properties.get("downloadedDateTime", datetime.min)

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
        return "microsoft.graph.PrintDocument"
