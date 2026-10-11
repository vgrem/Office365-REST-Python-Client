from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class GranularSiteRestoreArtifact(Entity):
    @property
    def site_id(self) -> Optional[str]:
        """Gets the siteId property"""
        return self.properties.get("siteId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.GranularSiteRestoreArtifact"
