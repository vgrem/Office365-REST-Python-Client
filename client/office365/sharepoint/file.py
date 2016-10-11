from client.office365.runtime.client_object import ClientObject
from client.office365.runtime.resource_path_entry import ResourcePathEntry
from client.office365.sharepoint.listitem import ListItem


class File(ClientObject):
    """Represents a file in a SharePoint Web site that can be a Web Part Page, an item in a document library,
    or a file in a folder."""

    @property
    def listitem_allfields(self):
        """Gets a value that specifies the list item field values for the list item corresponding to the file."""
        if self.is_property_available('ListItemAllFields'):
            return self.properties['ListItemAllFields']
        else:
            return ListItem(self.context, ResourcePathEntry(self.context, self.resource_path, "listItemAllFields"))


