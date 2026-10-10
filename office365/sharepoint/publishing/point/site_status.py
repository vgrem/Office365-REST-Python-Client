from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity


class PointPublishingSiteStatus(Entity):
    @property
    def entity_type_name(self):
        return "SP.Publishing.PointPublishingSiteStatus"

    @property
    def friendly_url(self) -> Optional[str]:
        """Gets the FriendlyUrl property"""
        return self.properties.get("FriendlyUrl", None)

    @property
    def site_id(self) -> Optional[UUID]:
        """Gets the SiteId property"""
        return self.properties.get("SiteId", None)

    @property
    def site_url(self) -> Optional[str]:
        """Gets the SiteUrl property"""
        return self.properties.get("SiteUrl", None)

    @property
    def status(self) -> Optional[int]:
        """Gets the Status property"""
        return self.properties.get("Status", None)
