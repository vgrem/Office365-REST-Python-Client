from office365.base_item import BaseItem
from office365.onedrive.list import List
from office365.onedrive.listItem import ListItem
from office365.runtime.resource_path import ResourcePath


class SharedDriveItem(BaseItem):
    """The sharedDriveItem resource is returned when using the Shares API to access a shared driveItem."""

    @property
    def listItem(self):
        """Used to access the underlying listItem"""
        return self.properties.get('listItem',
                                   ListItem(self.context, ResourcePath("listItem", self.resource_path)))

    @property
    def list(self):
        """Used to access the underlying list"""
        return self.properties.get('list',
                                   List(self.context, ResourcePath("list", self.resource_path)))
