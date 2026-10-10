from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection

if TYPE_CHECKING:
    from office365.sharepoint.sites.site import Site


class SPWebApplication(Entity):
    @property
    def display_name(self) -> Optional[str]:
        """Gets the DisplayName property"""
        return self.properties.get("DisplayName", None)

    @property
    def outbound_mail_port(self) -> Optional[int]:
        """Gets the OutboundMailPort property"""
        return self.properties.get("OutboundMailPort", None)

    @property
    def outbound_mail_reply_to_address(self) -> Optional[str]:
        """Gets the OutboundMailReplyToAddress property"""
        return self.properties.get("OutboundMailReplyToAddress", None)

    @property
    def outbound_mail_sender_address(self) -> Optional[str]:
        """Gets the OutboundMailSenderAddress property"""
        return self.properties.get("OutboundMailSenderAddress", None)

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Administration.SPWebApplication"

    @property
    def id(self) -> Optional[UUID]:
        """Gets the Id property"""
        return self.properties.get("Id", None)

    @property
    def sites(self) -> EntityCollection[Site]:
        """Gets the Sites property"""
        from office365.sharepoint.sites.site import Site

        return self.properties.get(
            "Sites", EntityCollection[Site](self.context, Site, ResourcePath("Sites", self.resource_path))
        )
