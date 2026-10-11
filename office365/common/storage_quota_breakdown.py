from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class StorageQuotaBreakdown(Entity):
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def manage_web_url(self) -> Optional[str]:
        """Gets the manageWebUrl property"""
        return self.properties.get("manageWebUrl", None)

    @property
    def used(self) -> Optional[int]:
        """Gets the used property"""
        return self.properties.get("used", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.StorageQuotaBreakdown"
