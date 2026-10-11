from __future__ import annotations

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection


class SiteProtectionUnitsBulkAdditionJob(Entity):
    @property
    def site_ids(self) -> StringCollection:
        """Gets the siteIds property"""
        return self.properties.get("siteIds", StringCollection())

    @property
    def site_web_urls(self) -> StringCollection:
        """Gets the siteWebUrls property"""
        return self.properties.get("siteWebUrls", StringCollection())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SiteProtectionUnitsBulkAdditionJob"
