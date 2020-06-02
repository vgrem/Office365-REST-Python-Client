from functools import partial

from office365.runtime.client_query import UpdateEntityQuery, DeleteEntityQuery
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.securable_object import SecurableObject


class ListItem(SecurableObject):
    """ListItem resource"""

    def update(self):
        """Update the list item."""
        self.ensure_type_name(self.parentList)
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)

    def validate_update_listItem(self, form_values, new_document_update):
        """Validates and sets the values of the specified collection of fields for the list item."""
        qry = ServiceOperationQuery(self,
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
                                    "systemUpdate")
        self.context.add_query(qry)

    def update_overwrite_version(self):
        """Update the list item."""
        qry = ServiceOperationQuery(self,
                                    HttpMethod.Post,
                                    "updateOverwriteVersion")
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the ListItem."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)

    @property
    def parentList(self):
        """Get parent List"""
        if self.is_property_available("ParentList"):
            return self.properties["ParentList"]
        else:
            from office365.sharepoint.list import List
            return List(self.context, ResourcePath("ParentList", self.resource_path))

    @property
    def file(self):
        """Get file"""
        if self.is_property_available("File"):
            return self.properties["File"]
        else:
            from office365.sharepoint.file import File
            return File(self.context, ResourcePath("File", self.resource_path))

    @property
    def folder(self):
        """Get folder"""
        if self.is_property_available("Folder"):
            return self.properties["Folder"]
        else:
            from office365.sharepoint.folder import Folder
            return Folder(self.context, ResourcePath("Folder", self.resource_path))

    @property
    def attachmentFiles(self):
        """Get attachment files"""
        if self.is_property_available('AttachmentFiles'):
            return self.properties["AttachmentFiles"]
        else:
            from office365.sharepoint.attachmentfile_collection import AttachmentFileCollection
            return AttachmentFileCollection(self.context,
                                            ResourcePath("AttachmentFiles", self.resource_path))

    def set_property(self, name, value, persist_changes=True):
        super(ListItem, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Id":
                self._resource_path = ResourcePathServiceOperation(
                    "getItemById", [value], self._parent_collection.resource_path.parent)

    def ensure_type_name(self, target_list):
        if not self._entity_type_name:
            target_list.ensure_property("ListItemEntityTypeFullName", self._init_item_type)

    def _init_item_type(self, target_list):
        self._entity_type_name = target_list.properties['ListItemEntityTypeFullName']
