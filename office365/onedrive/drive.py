from office365.base_item import BaseItem
from office365.onedrive.driveItem import DriveItem
from office365.onedrive.driveItemCollection import DriveItemCollection
from office365.onedrive.list import List
from office365.onedrive.root_resource_path import RootResourcePath
from office365.runtime.resource_path import ResourcePath


class Drive(BaseItem):
    """The drive resource is the top level object representing a user's OneDrive or a document library in
    SharePoint. """

    @property
    def shared_with_me(self):
        """Retrieve a collection of DriveItem resources that have been shared with the owner of the Drive."""
        return self.properties.get('sharedWithMe',
                                   DriveItemCollection(self.context, ResourcePath("sharedWithMe", self.resource_path)))

    @property
    def root(self):
        """The root folder of the drive."""
        return self.properties.get('root', DriveItem(self.context, RootResourcePath(self.resource_path)))

    @property
    def list(self):
        """For drives in SharePoint, the underlying document library list."""
        return self.properties.get('list', List(self.context, ResourcePath("list", self.resource_path)))

    @property
    def items(self):
        """All items contained in the drive."""
        return self.properties.get('items',
                                   DriveItemCollection(self.context, ResourcePath("items", self.resource_path)))
