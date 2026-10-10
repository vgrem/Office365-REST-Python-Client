from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.contentsolution.template_api import TemplateAPI


class ContentSolution(Entity):
    @property
    def templates(self) -> TemplateAPI:
        """Gets the Templates property"""
        from office365.sharepoint.contentsolution.template_api import TemplateAPI

        return self.properties.get("Templates", TemplateAPI(self.context, ResourcePath("Templates", self.resource_path)))
