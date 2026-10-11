from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity


class NamedLocation(Entity):
    """This is the base class that represents a Microsoft Entra ID named location.
    Named locations are custom rules that define network locations which can then be used
    in a Conditional Access policy."""

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def id(self) -> Optional[str]:
        """Gets the id property"""
        return self.properties.get("id", None)

    @property
    def modified_date_time(self) -> Optional[datetime]:
        """Gets the modifiedDateTime property"""
        return self.properties.get("modifiedDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.NamedLocation"
