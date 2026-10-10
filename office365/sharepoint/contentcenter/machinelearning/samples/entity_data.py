from __future__ import annotations

from typing import Optional

from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity


class SPMachineLearningSampleEntityData(Entity):
    def __init__(self, context):
        static_path = ResourcePath("Microsoft.Office.Server.ContentCenter.SPMachineLearningSampleEntityData")
        super().__init__(context, static_path)

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.ContentCenter.SPMachineLearningSampleEntityData"

    @property
    def extracted_text(self) -> Optional[str]:
        """Gets the ExtractedText property"""
        return self.properties.get("ExtractedText", None)

    @property
    def markups(self) -> Optional[str]:
        """Gets the Markups property"""
        return self.properties.get("Markups", None)
