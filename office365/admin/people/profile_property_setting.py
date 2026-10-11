from __future__ import annotations

from typing import Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection


class ProfilePropertySetting(Entity):
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the name property"""
        return self.properties.get("name", None)

    @property
    def prioritized_source_urls(self) -> StringCollection:
        """Gets the prioritizedSourceUrls property"""
        return self.properties.get("prioritizedSourceUrls", StringCollection())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ProfilePropertySetting"
