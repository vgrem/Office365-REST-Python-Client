from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity


class TeamSiteData(Entity):
    """"""

    @property
    def error_tag(self) -> Optional[int]:
        """Gets the ErrorTag property"""
        return self.properties.get("ErrorTag", None)

    @property
    def header_color_index_in_dark_mode(self) -> Optional[int]:
        """Gets the HeaderColorIndexInDarkMode property"""
        return self.properties.get("HeaderColorIndexInDarkMode", None)

    @property
    def header_color_index_in_light_mode(self) -> Optional[int]:
        """Gets the HeaderColorIndexInLightMode property"""
        return self.properties.get("HeaderColorIndexInLightMode", None)

    @property
    def header_emphasis(self) -> Optional[int]:
        """Gets the HeaderEmphasis property"""
        return self.properties.get("HeaderEmphasis", None)

    @property
    def hub_site_id(self) -> Optional[UUID]:
        """Gets the HubSiteId property"""
        return self.properties.get("HubSiteId", None)

    @property
    def site_url(self) -> Optional[str]:
        """Gets the SiteUrl property"""
        return self.properties.get("SiteUrl", None)

    @property
    def tenant_instance_id(self) -> Optional[UUID]:
        """Gets the TenantInstanceId property"""
        return self.properties.get("TenantInstanceId", None)

    @property
    def theme_token(self) -> Optional[str]:
        """Gets the ThemeToken property"""
        return self.properties.get("ThemeToken", None)
