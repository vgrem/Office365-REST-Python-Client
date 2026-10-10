from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class HostedAppAddResponse(Entity):
    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.ClientSideComponent.HostedAppAddResponse"

    @property
    def item_id(self) -> Optional[int]:
        """Gets the itemId property"""
        return self.properties.get("itemId", None)

    @property
    def share_link_url(self) -> Optional[str]:
        """Gets the shareLinkUrl property"""
        return self.properties.get("shareLinkUrl", None)

    @property
    def share_web_path(self) -> Optional[str]:
        """Gets the shareWebPath property"""
        return self.properties.get("shareWebPath", None)
