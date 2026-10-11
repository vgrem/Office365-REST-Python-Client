from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.admin.browser_site_list import BrowserSiteList


class InternetExplorerMode(Entity):
    @property
    def site_lists(self) -> EntityCollection[BrowserSiteList]:
        """Gets the siteLists property"""
        from office365.admin.browser_site_list import BrowserSiteList

        return self.properties.get(
            "siteLists",
            EntityCollection[BrowserSiteList](
                self.context, BrowserSiteList, ResourcePath("siteLists", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.InternetExplorerMode"
