from client.folder_collection import FolderCollection
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

    def update(self):
        qry = ClientQuery.create_update_query(self, self.to_json())
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the folder."""
        qry = ClientQuery.create_delete_query(self)
        self.context.add_query(qry)
        # self.removeFromParentCollection()

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

    @property
    def folders(self):
        """Get a folder collection"""
        if self.is_property_available('Folders'):
            return self.properties["Folders"]
        else:
            return FolderCollection(self.context, "folders", self.resource_path)
