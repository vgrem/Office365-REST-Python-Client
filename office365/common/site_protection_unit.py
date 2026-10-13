from __future__ import annotations

from typing import Optional

from office365.backuprestore.protection_unit_base import ProtectionUnitBase


class SiteProtectionUnit(ProtectionUnitBase):
    @property
    def site_id(self) -> Optional[str]:
        """Gets the siteId property"""
        return self.properties.get("siteId", None)

    @property
    def site_name(self) -> Optional[str]:
        """Gets the siteName property"""
        return self.properties.get("siteName", None)

    @property
    def site_web_url(self) -> Optional[str]:
        """Gets the siteWebUrl property"""
        return self.properties.get("siteWebUrl", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SiteProtectionUnit"
