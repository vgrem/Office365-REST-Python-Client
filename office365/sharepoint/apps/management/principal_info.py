from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class SPAppPrincipalInfo(Entity):
    """"""

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.AppManagement.SPAppPrincipalInfo"

    @property
    def flag(self) -> Optional[int]:
        """Gets the Flag property"""
        return self.properties.get("Flag", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the Name property"""
        return self.properties.get("Name", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)
