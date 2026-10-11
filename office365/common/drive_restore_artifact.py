from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class DriveRestoreArtifact(Entity):
    @property
    def restored_site_id(self) -> Optional[str]:
        """Gets the restoredSiteId property"""
        return self.properties.get("restoredSiteId", None)

    @property
    def restored_site_name(self) -> Optional[str]:
        """Gets the restoredSiteName property"""
        return self.properties.get("restoredSiteName", None)

    @property
    def restored_site_web_url(self) -> Optional[str]:
        """Gets the restoredSiteWebUrl property"""
        return self.properties.get("restoredSiteWebUrl", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DriveRestoreArtifact"
