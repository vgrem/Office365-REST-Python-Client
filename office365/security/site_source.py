from __future__ import annotations

from office365.entity import Entity
from office365.onedrive.sites.site import Site
from office365.runtime.paths.resource_path import ResourcePath


class SiteSource(Entity):
    @property
    def site(self) -> Site:
        """Gets the site property"""
        return self.properties.get("site", Site(self.context, ResourcePath("site", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.SiteSource"
