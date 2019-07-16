from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import ClientQuery
from office365.runtime.odata.odata_path_parser import ODataPathParser
from office365.runtime.resource_path_entry import ResourcePathEntry
from office365.sharepoint.listitem import ListItem


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
            from office365.sharepoint.file_collection import FileCollection
            return FileCollection(self.context, ResourcePathEntry(self.context, self.resource_path, "Files"))

    @property
    def folders(self):
        """Get a folder collection"""
        if self.is_property_available('Folders'):
            return self.properties["Folders"]
        else:
            from office365.sharepoint.folder_collection import FolderCollection
            return FolderCollection(self.context, ResourcePathEntry(self.context, self.resource_path, "Folders"))

    @property
    def resource_path(self):
        resource_path = super(Folder, self).resource_path
        if resource_path:
            return resource_path

        # fallback: create a new resource path
        if self.is_property_available("ServerRelativeUrl"):
            self._resource_path = ResourcePathEntry(
                self.context,
                ResourcePathEntry.from_uri("Web", self.context),
                ODataPathParser.from_method("GetFolderByServerRelativeUrl", [self.properties["ServerRelativeUrl"]]))
        elif self.is_property_available("UniqueId"):
            self._resource_path = ResourcePathEntry(
                self.context,
                ResourcePathEntry.from_uri("Web", self.context),
                ODataPathParser.from_method("GetFolderById", [{'guid': self.properties["UniqueId"]}]))
        return self._resource_path
