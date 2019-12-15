from office365.runtime.resource_path_entity import ResourcePathEntity
from office365.onedrive.baseItem import BaseItem
from office365.onedrive.fieldValueSet import FieldValueSet


class ListItem(BaseItem):
    """Represents an item in a SharePoint list. Column values in the list are available through the fieldValueSet
    dictionary. """

    @property
    def fields(self):
        """The values of the columns set on this list item."""
        if self.is_property_available('fields'):
            return self.properties['fields']
        else:
            return FieldValueSet(self.context, ResourcePathEntity(self.context, self.resourcePath, "fields"))

    @property
    def driveItem(self):
        """For document libraries, the driveItem relationship exposes the listItem as a driveItem."""
        if self.is_property_available('driveItem'):
            return self.properties['driveItem']
        else:
            from office365.onedrive.driveItem import DriveItem
            return DriveItem(self.context, ResourcePathEntity(self.context, self.resourcePath, "driveItem"))
