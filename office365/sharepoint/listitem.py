from office365.runtime.client_query import ClientQuery
from office365.runtime.odata.odata_path_parser import ODataPathParser
from office365.runtime.resource_path_entity import ResourcePathEntity
from office365.sharepoint.securable_object import SecurableObject


class ListItem(SecurableObject):
    """ListItem client object resource"""

    def update(self):
        """Update the list."""
        qry = ClientQuery.update_entry_query(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the list."""
        qry = ClientQuery.delete_entry_query(self)
        self.context.add_query(qry)

    @property
    def file(self):
        """Get file"""
        if self.is_property_available("File"):
            return self.properties["File"]
        else:
            from office365.sharepoint.file import File
            return File(self.context, ResourcePathEntity(self.context, self.resource_path, "File"))

    @property
    def folder(self):
        """Get folder"""
        if self.is_property_available("Folder"):
            return self.properties["Folder"]
        else:
            from office365.sharepoint.folder import Folder
            return Folder(self.context, ResourcePathEntity(self.context, self.resource_path, "Folder"))

    @property
    def attachment_files(self):
        """Get attachment files"""
        if self.is_property_available('AttachmentFiles'):
            return self.properties["AttachmentFiles"]
        else:
            from office365.sharepoint.attachmentfile_collection import AttachmentfileCollection
            return AttachmentfileCollection(self.context,
                                            ResourcePathEntity(self.context, self.resource_path, "AttachmentFiles"))

    @property
    def resource_path(self):
        resource_path = super(ListItem, self).resource_path
        if resource_path:
            return resource_path

        # fallback: create a new resource path
        if self.is_property_available("Id"):
            self._resource_path = ResourcePathEntity(
                self.context,
                self._parent_collection.resource_path,
                ODataPathParser.from_method("getItemById", [self.properties["Id"]]))

        return self._resource_path
