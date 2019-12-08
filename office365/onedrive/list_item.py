from office365.runtime.resource_path_entity import ResourcePathEntity
from office365.onedrive.base_item import BaseItem


class ListItem(BaseItem):
    """Represents an item in a SharePoint list. Column values in the list are available through the fieldValueSet
    dictionary. """

    @property
    def driveItem(self):
        """For document libraries, the driveItem relationship exposes the listItem as a driveItem."""
        if self.is_property_available('driveItem'):
            return self.properties['driveItem']
        else:
            from office365.onedrive.drive_item import DriveItem
            return DriveItem(self.context, ResourcePathEntity(self.context, self.resource_path, "driveItem"))
