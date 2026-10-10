from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity


class UnifiedGroup(Entity):
    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.MultiGeo.Service.UnifiedGroup"

    @property
    def display_name(self) -> Optional[str]:
        """Gets the DisplayName property"""
        return self.properties.get("DisplayName", None)

    @property
    def group_alias(self) -> Optional[str]:
        """Gets the GroupAlias property"""
        return self.properties.get("GroupAlias", None)

    @property
    def mail(self) -> Optional[str]:
        """Gets the Mail property"""
        return self.properties.get("Mail", None)

    @property
    def object_id(self) -> Optional[UUID]:
        """Gets the ObjectId property"""
        return self.properties.get("ObjectId", None)

    @property
    def preferred_data_location(self) -> Optional[str]:
        """Gets the PreferredDataLocation property"""
        return self.properties.get("PreferredDataLocation", None)

    @property
    def site_url(self) -> Optional[str]:
        """Gets the SiteUrl property"""
        return self.properties.get("SiteUrl", None)
