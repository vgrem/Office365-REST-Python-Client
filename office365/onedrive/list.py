from office365.base_item import BaseItem
from office365.onedrive.columnDefinitionCollection import ColumnDefinitionCollection
from office365.onedrive.contentTypeCollection import ContentTypeCollection
from office365.onedrive.listItemCollection import ListItemCollection
from office365.runtime.resource_path import ResourcePath


class List(BaseItem):
    """The list resource represents a list in a site. This resource contains the top level properties of the list,
    including template and field definitions. """

    @property
    def sharepointids(self):
        """Returns identifiers useful for SharePoint REST compatibility."""
        return self.properties.get('sharepointIds', None)

    @property
    def drive(self):
        """Only present on document libraries. Allows access to the list as a drive resource with driveItems."""
        from office365.onedrive.drive import Drive
        return self.properties.get('drive',
                                   Drive(self.context, ResourcePath("drive", self.resource_path)))

    @property
    def columns(self):
        """The collection of columns under this site."""
        return self.properties.get('columns',
                                   ColumnDefinitionCollection(self.context,
                                                              ResourcePath("columns", self.resource_path)))

    @property
    def contentTypes(self):
        """The collection of content types under this site."""
        return self.properties.get('contentTypes',
                                   ContentTypeCollection(self.context,
                                                         ResourcePath("contentTypes", self.resource_path)))

    @property
    def items(self):
        """All items contained in the list."""
        return self.properties.get('items',
                                   ListItemCollection(self.context, ResourcePath("items", self.resource_path)))
