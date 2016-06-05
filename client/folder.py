from client.listitem import ListItem
from client.runtime.client_action_type import ClientActionType
from client.runtime.client_query import ClientQuery
from client_object import ClientObject
from client.file_collection import FileCollection


class Folder(ClientObject):
    """Represents a folder in a SharePoint Web site."""

    def rename(self, name):
        """Rename a Folder resource"""
        item = self.list_item_all_fields
        item.properties['Title'] = name
        item.properties['FileLeafRef'] = name
        qry = ClientQuery(item.url, ClientActionType.Update, item)
        self.context.add_query(qry, self)

    @property
    def list_item_all_fields(self):
        """Specifies the list item field (2) values for the list item corresponding to the folder."""
        if self.is_property_available('ListItemAllFields'):
            return self.properties["ListItemAllFields"]
        else:
            return ListItem(self.context, "ListItemAllFields", self.resource_path)

    @property
    def files(self):
        """Get a file collection"""
        if self.is_property_available('Files'):
            return self.properties["Files"]
        else:
            return FileCollection(self.context, "files", self.resource_path)
