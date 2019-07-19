from office365.onedrive.base_item import BaseItem
from office365.onedrive.drive_item import DriveItem
from office365.runtime.resource_path_entity import ResourcePathEntity


class Drive(BaseItem):
    """The drive resource is the top level object representing a user's OneDrive or a document library in
    SharePoint. """

    @property
    def root(self):
        """The root folder of the drive."""
        if self.is_property_available("root"):
            return self.properties['root']
        else:
            return DriveItem(self.context, ResourcePathEntity(self.context, self.resource_path, "root"))

    @property
    def items(self):
        """All items contained in the drive."""
        if self.is_property_available("items"):
            return self.properties['items']
        else:
            return None
