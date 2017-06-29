from office365.sharepoint.file_collection import FileCollection
from office365.sharepoint.listitem import ListItem
from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import ClientQuery
from office365.runtime.resource_path_entry import ResourcePathEntry
from office365.sharepoint.folder_collection import FolderCollection


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

    @property
    def resource_path(self):
        orig_path = ClientObject.resource_path.fget(self)
        if self.is_property_available("ServerRelativeUrl") and orig_path is None:
            return ResourcePathEntry(self.context,
                                     self.context.web.resource_path,
                                     "GetFolderByServerRelativeUrl('{0}')".format(self.properties["ServerRelativeUrl"]))
        elif self.is_property_available("UniqueId") and orig_path is None:
            return ResourcePathEntry(self.context,
                                     self.context.web.resource_path,
                                     "GetFolderById(guid'{0}')".format(self.properties["UniqueId"]))
        return orig_path
