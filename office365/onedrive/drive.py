from office365.onedrive.baseItem import BaseItem
from office365.onedrive.driveItem import DriveItem
from office365.onedrive.driveItemCollection import DriveItemCollection
from office365.onedrive.list import List
from office365.runtime.resource_path import ResourcePath


class Drive(BaseItem):
    """The drive resource is the top level object representing a user's OneDrive or a document library in
    SharePoint. """

    @property
    def root(self):
        """The root folder of the drive."""
        if self.is_property_available("root"):
            return self.properties['root']
        else:
            return DriveItem(self.context, ResourcePath("root", self.resourcePath))

    @property
    def list(self):
        """For drives in SharePoint, the underlying document library list."""
        if self.is_property_available("list"):
            return self.properties['list']
        else:
            return List(self.context, ResourcePath("list", self.resourcePath))

    @property
    def items(self):
        """All items contained in the drive."""
        if self.is_property_available("items"):
            return self.properties['items']
        else:
            return DriveItemCollection(self.context, ResourcePath("items", self.resourcePath))
