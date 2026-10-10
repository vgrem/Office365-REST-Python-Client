from __future__ import annotations

from typing import Optional

from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.entity import Entity
from office365.sharepoint.migrationcenter.folderinformation import SPFolderInformation


class ChannelResource(Entity):
    """"""

    @property
    def absolute_url(self) -> Optional[str]:
        """Gets the AbsoluteUrl property"""
        return self.properties.get("AbsoluteUrl", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the Description property"""
        return self.properties.get("Description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the DisplayName property"""
        return self.properties.get("DisplayName", None)

    @property
    def membership_type(self) -> Optional[str]:
        """Gets the MembershipType property"""
        return self.properties.get("MembershipType", None)

    @property
    def server_relative_url(self) -> Optional[str]:
        """Gets the ServerRelativeUrl property"""
        return self.properties.get("ServerRelativeUrl", None)

    @property
    def sub_folders(self) -> ClientValueCollection[SPFolderInformation]:
        """Gets the SubFolders property"""
        return self.properties.get("SubFolders", ClientValueCollection(SPFolderInformation))

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.MigrationCenter.Common.Teams.ChannelResource"

    @property
    def id(self) -> Optional[str]:
        """Gets the Id property"""
        return self.properties.get("Id", None)
