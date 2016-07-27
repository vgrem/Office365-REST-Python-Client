from client.file_collection import FileCollection
from client.folder_collection import FolderCollection
from client.listitem import ListItem
from client.runtime.client_object import ClientObject
from client.runtime.client_query import ClientQuery
from client.runtime.resource_path_entry import ResourcePathEntry


class Folder(ClientObject):
    """Represents a folder in a SharePoint Web site."""

    def rename(self, name):
        """Rename a Folder resource"""
        item = self.list_item_all_fields
        item.properties['Title'] = name
        item.properties['FileLeafRef'] = name
        qry = ClientQuery.update_entry_query(item)
        self.context.add_query(qry, self)

    def update(self):
        qry = ClientQuery.update_entry_query(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the folder."""
        qry = ClientQuery.delete_entry_query(self)
        self.context.add_query(qry)
        # self.removeFromParentCollection()

    @property
    def list_item_all_fields(self):
        """Specifies the list item field (2) values for the list item corresponding to the folder."""
        if self.is_property_available('ListItemAllFields'):
            return self.properties["ListItemAllFields"]
        else:
            return ListItem(self.context, ResourcePathEntry(self.context, self.resource_path, "ListItemAllFields"))

    @property
    def files(self):
        """Get a file collection"""
        if self.is_property_available('Files'):
            return self.properties["Files"]
        else:
            return FileCollection(self.context, ResourcePathEntry(self.context, self.resource_path, "Files"))

    @property
    def folders(self):
        """Get a folder collection"""
        if self.is_property_available('Folders'):
            return self.properties["Folders"]
        else:
            return FolderCollection(self.context, ResourcePathEntry(self.context, self.resource_path, "Folders"))
