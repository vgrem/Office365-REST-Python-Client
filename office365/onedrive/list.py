from office365.onedrive.baseItem import BaseItem
from office365.onedrive.listItemCollection import ListItemCollection
from office365.runtime.resource_path_entity import ResourcePathEntity


class List(BaseItem):
    """The list resource represents a list in a site. This resource contains the top level properties of the list,
    including template and field definitions. """

    @property
    def drive(self):
        """Only present on document libraries. Allows access to the list as a drive resource with driveItems."""
        if self.is_property_available('drive'):
            return self.properties['drive']
        else:
            from office365.onedrive.drive import Drive
            return Drive(self.context, ResourcePathEntity(self.context, self.resourcePath, "drive"))

    @property
    def items(self):
        """All items contained in the list."""
        if self.is_property_available('items'):
            return self.properties['items']
        else:
            return ListItemCollection(self.context, ResourcePathEntity(self.context, self.resourcePath, "items"))
