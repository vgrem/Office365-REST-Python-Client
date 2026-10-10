from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity


class SmartCacheItem(Entity):
    """ """

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.SmartCache.SmartCacheItem"

    @property
    def access_url(self) -> Optional[str]:
        """Gets the accessUrl property"""
        return self.properties.get("accessUrl", None)

    @property
    def container_title(self) -> Optional[str]:
        """Gets the containerTitle property"""
        return self.properties.get("containerTitle", None)

    @property
    def content_class(self) -> Optional[str]:
        """Gets the contentClass property"""
        return self.properties.get("contentClass", None)

    @property
    def is_default_document_library(self) -> Optional[bool]:
        """Gets the isDefaultDocumentLibrary property"""
        return self.properties.get("isDefaultDocumentLibrary", None)

    @property
    def is_teams_channel_site(self) -> Optional[bool]:
        """Gets the isTeamsChannelSite property"""
        return self.properties.get("isTeamsChannelSite", None)

    @property
    def is_teams_connected_site(self) -> Optional[bool]:
        """Gets the isTeamsConnectedSite property"""
        return self.properties.get("isTeamsConnectedSite", None)

    @property
    def last_access_datetime(self) -> Optional[datetime]:
        """Gets the lastAccessDateTime property"""
        return self.properties.get("lastAccessDateTime", datetime.min)

    @property
    def list_id(self) -> Optional[UUID]:
        """Gets the listId property"""
        return self.properties.get("listId", None)

    @property
    def list_item_id(self) -> Optional[int]:
        """Gets the listItemId property"""
        return self.properties.get("listItemId", None)

    @property
    def operation(self) -> Optional[int]:
        """Gets the operation property"""
        return self.properties.get("operation", None)

    @property
    def pin_order(self) -> Optional[int]:
        """Gets the pinOrder property"""
        return self.properties.get("pinOrder", None)

    @property
    def site_acronym(self) -> Optional[str]:
        """Gets the siteAcronym property"""
        return self.properties.get("siteAcronym", None)

    @property
    def site_color(self) -> Optional[str]:
        """Gets the siteColor property"""
        return self.properties.get("siteColor", None)

    @property
    def site_id(self) -> Optional[UUID]:
        """Gets the siteId property"""
        return self.properties.get("siteId", None)

    @property
    def site_logo_url(self) -> Optional[str]:
        """Gets the siteLogoUrl property"""
        return self.properties.get("siteLogoUrl", None)

    @property
    def spo_id(self) -> Optional[str]:
        """Gets the spoId property"""
        return self.properties.get("spoId", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the title property"""
        return self.properties.get("title", None)

    @property
    def unique_id(self) -> Optional[UUID]:
        """Gets the uniqueId property"""
        return self.properties.get("uniqueId", None)

    @property
    def web_id(self) -> Optional[UUID]:
        """Gets the webId property"""
        return self.properties.get("webId", None)

    @property
    def web_url(self) -> Optional[str]:
        """Gets the webUrl property"""
        return self.properties.get("webUrl", None)
