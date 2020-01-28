from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import UpdateEntityQuery, DeleteEntityQuery
from office365.runtime.odata.odata_path_parser import ODataPathParser
from office365.runtime.resource_path_entity import ResourcePathEntity
from office365.sharepoint.listitem import ListItem


class Folder(ClientObject):
    """Represents a folder in a SharePoint Web site."""

    def rename(self, name):
        """Rename a Folder resource"""
        item = self.list_item_all_fields
        item.properties['Title'] = name
        item.properties['FileLeafRef'] = name
        qry = UpdateEntityQuery(item)
        self.context.add_query(qry, self)

    def update(self):
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the folder."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        # self.removeFromParentCollection()

    @property
    def list_item_all_fields(self):
        """Specifies the list item field (2) values for the list item corresponding to the folder."""
        if self.is_property_available('ListItemAllFields'):
            return self.properties["ListItemAllFields"]
        else:
            return ListItem(self.context, ResourcePathEntity(self.context, self.resourcePath, "ListItemAllFields"))

    @property
    def files(self):
        """Get a file collection"""
        if self.is_property_available('Files'):
            return self.properties["Files"]
        else:
            from office365.sharepoint.file_collection import FileCollection
            return FileCollection(self.context, ResourcePathEntity(self.context, self.resourcePath, "Files"))

    @property
    def folders(self):
        """Get a folder collection"""
        if self.is_property_available('Folders'):
            return self.properties["Folders"]
        else:
            from office365.sharepoint.folder_collection import FolderCollection
            return FolderCollection(self.context, ResourcePathEntity(self.context, self.resourcePath, "Folders"))

    def set_property(self, name, value, serializable=True):
        super(Folder, self).set_property(name, value, serializable)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "ServerRelativeUrl":
                self._resource_path = ResourcePathEntity(
                    self.context,
                    ResourcePathEntity.from_uri("Web", self.context),
                    ODataPathParser.from_method("GetFolderByServerRelativeUrl", [value]))
            elif name == "UniqueId":
                self._resource_path = ResourcePathEntity(
                    self.context,
                    ResourcePathEntity.from_uri("Web", self.context),
                    ODataPathParser.from_method("GetFolderById", [value]))

