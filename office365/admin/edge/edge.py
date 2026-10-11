from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.admin.internet_explorer_mode import InternetExplorerMode


class Edge(Entity):
    @property
    def internet_explorer_mode(self) -> InternetExplorerMode:
        """Gets the internetExplorerMode property"""
        from office365.admin.internet_explorer_mode import InternetExplorerMode

        return self.properties.get(
            "internetExplorerMode",
            InternetExplorerMode(self.context, ResourcePath("internetExplorerMode", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Edge"
