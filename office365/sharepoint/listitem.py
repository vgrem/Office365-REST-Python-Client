from office365.runtime.client_query import UpdateEntityQuery, DeleteEntityQuery, ServiceOperationQuery
from office365.runtime.odata.odata_path_parser import ODataPathParser
from office365.runtime.resource_path_entity import ResourcePathEntity
from office365.runtime.utilities.http_method import HttpMethod
from office365.sharepoint.securable_object import SecurableObject


class ListItem(SecurableObject):
    """ListItem resource"""

    def update(self):
        """Update the list item."""
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)

    def validate_update_listItem(self, form_values, new_document_update):
        """Validates and sets the values of the specified collection of fields for the list item."""
        qry = ServiceOperationQuery(self,
                                    HttpMethod.Post,
                                    "validateUpdateListItem",
                                    None,
                                    {
                                        "formValues": form_values,
                                        "bNewDocumentUpdate": new_document_update,
                                    })
        self.context.add_query(qry)

    def system_update(self):
        """Update the list item."""
        qry = ServiceOperationQuery(self,
                                    HttpMethod.Post,
                                    "systemUpdate")
        self.context.add_query(qry)

    def update_overwrite_version(self):
        """Update the list item."""
        qry = ServiceOperationQuery(self,
                                    HttpMethod.Post,
                                    "updateOverwriteVersion")
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the list."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)

    @property
    def parentList(self):
        """Get parent List"""
        if self.is_property_available("ParentList"):
            return self.properties["ParentList"]
        else:
            from office365.sharepoint.list import List
            return List(self.context, ResourcePathEntity(self.context, self.resourcePath, "ParentList"))

    @property
    def file(self):
        """Get file"""
        if self.is_property_available("File"):
            return self.properties["File"]
        else:
            from office365.sharepoint.file import File
            return File(self.context, ResourcePathEntity(self.context, self.resourcePath, "File"))

    @property
    def folder(self):
        """Get folder"""
        if self.is_property_available("Folder"):
            return self.properties["Folder"]
        else:
            from office365.sharepoint.folder import Folder
            return Folder(self.context, ResourcePathEntity(self.context, self.resourcePath, "Folder"))

    @property
    def attachmentFiles(self):
        """Get attachment files"""
        if self.is_property_available('AttachmentFiles'):
            return self.properties["AttachmentFiles"]
        else:
            from office365.sharepoint.attachmentfile_collection import AttachmentfileCollection
            return AttachmentfileCollection(self.context,
                                            ResourcePathEntity(self.context, self.resourcePath, "AttachmentFiles"))

    @property
    def resourcePath(self):
        resource_path = super(ListItem, self).resourcePath
        if resource_path:
            return resource_path

        # fallback: create a new resource path
        if self.is_property_available("Id"):
            self._resource_path = ResourcePathEntity(
                self.context,
                self._parent_collection.resourcePath,
                ODataPathParser.from_method("getItemById", [self.properties["Id"]]))

        return self._resource_path
