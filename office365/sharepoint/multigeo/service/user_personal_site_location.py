from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity


class UserPersonalSiteLocation(Entity):
    """"""

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.MultiGeo.Service.UserPersonalSiteLocation"

    @property
    def location(self) -> Optional[str]:
        """Gets the Location property"""
        return self.properties.get("Location", None)

    @property
    def my_site_url(self) -> Optional[str]:
        """Gets the MySiteUrl property"""
        return self.properties.get("MySiteUrl", None)

    @property
    def preferred_data_location(self) -> Optional[str]:
        """Gets the PreferredDataLocation property"""
        return self.properties.get("PreferredDataLocation", None)

    @property
    def site_id(self) -> Optional[UUID]:
        """Gets the SiteId property"""
        return self.properties.get("SiteId", None)

    @property
    def user_principal_name(self) -> Optional[str]:
        """Gets the UserPrincipalName property"""
        return self.properties.get("UserPrincipalName", None)
