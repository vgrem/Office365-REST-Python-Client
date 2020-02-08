from office365.onedrive.baseItem import BaseItem
from office365.runtime.resource_path import ResourcePath
from office365.onedrive.columnDefinitionCollection import ColumnDefinitionCollection
from office365.onedrive.contentTypeCollection import ContentTypeCollection
from office365.onedrive.listItemCollection import ListItemCollection


class List(BaseItem):
    """The list resource represents a list in a site. This resource contains the top level properties of the list,
    including template and field definitions. """

    @property
    def sharepointids(self):
        """Returns identifiers useful for SharePoint REST compatibility."""
        if self.is_property_available("sharepointIds"):
            return self.properties['sharepointIds']
        return None

    @property
    def drive(self):
        """Only present on document libraries. Allows access to the list as a drive resource with driveItems."""
        if self.is_property_available('drive'):
            return self.properties['drive']
        else:
            from office365.onedrive.drive import Drive
            return Drive(self.context, ResourcePath("drive", self.resourcePath))

    @property
    def columns(self):
        """The collection of columns under this site."""
        if self.is_property_available('columns'):
            return self.properties['columns']
        else:
            return ColumnDefinitionCollection(self.context,
                                              ResourcePath("columns", self.resourcePath))

    @property
    def contentTypes(self):
        """The collection of content types under this site."""
        if self.is_property_available('contentTypes'):
            return self.properties['contentTypes']
        else:
            return ContentTypeCollection(self.context,
                                         ResourcePath("contentTypes", self.resourcePath))

    @property
    def items(self):
        """All items contained in the list."""
        if self.is_property_available('items'):
            return self.properties['items']
        else:
            return ListItemCollection(self.context, ResourcePath("items", self.resourcePath))
