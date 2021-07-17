from office365.base_item import BaseItem
from office365.entity_collection import EntityCollection
from office365.onedrive.fieldValueSet import FieldValueSet
from office365.onedrive.listItemVersion import ListItemVersion
from office365.runtime.resource_path import ResourcePath


class ListItem(BaseItem):
    """Represents an item in a SharePoint list. Column values in the list are available through the fieldValueSet
    dictionary. """

    @property
    def fields(self):
        """The values of the columns set on this list item."""
        return self.properties.get('fields',
                                   FieldValueSet(self.context, ResourcePath("fields", self.resource_path)))

    @property
    def versions(self):
        """The list of previous versions of the list item."""
        return self.properties.get('versions',
                                   EntityCollection(self.context, ListItemVersion,
                                                    ResourcePath("versions", self.resource_path)))

    @property
    def drive_item(self):
        """For document libraries, the driveItem relationship exposes the listItem as a driveItem."""
        from office365.onedrive.driveItem import DriveItem
        return self.properties.get('driveItem', DriveItem(self.context, ResourcePath("driveItem", self.resource_path)))
