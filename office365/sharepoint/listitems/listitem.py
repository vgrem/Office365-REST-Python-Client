from office365.runtime.client_query import DeleteEntityQuery, UpdateEntityQuery
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.fields.fieldLookupValue import FieldLookupValue
from office365.sharepoint.fields.fieldMultiLookupValue import FieldMultiLookupValue
from office365.sharepoint.permissions.securable_object import SecurableObject
from office365.sharepoint.sharing.externalSharingSiteOption import ExternalSharingSiteOption
from office365.sharepoint.sharing.objectSharingInformation import ObjectSharingInformation
from office365.sharepoint.sharing.sharingResult import SharingResult
from office365.sharepoint.ui.applicationpages.clientPeoplePickerQueryParameters import ClientPeoplePickerQueryParameters
from office365.sharepoint.ui.applicationpages.clientPeoplePickerWebServiceInterface import (
    ClientPeoplePickerWebServiceInterface,
)


class ListItem(SecurableObject):
    """An individual entry within a SharePoint list. Each list item has a schema that maps to fields in the list
    that contains the item, depending on the content type of the item."""

    def share(self, user_principal_name,
              shareOption=ExternalSharingSiteOption.View,
              sendEmail=True, emailSubject=None, emailBody=None):
        """
        Share a ListItem (file or folder facet)

        :param str user_principal_name: User identifier
        :param ExternalSharingSiteOption shareOption: The sharing type of permission to grant on the object.
        :param bool sendEmail: A flag to determine if an email notification SHOULD be sent (if email is configured).
        :param str emailSubject: The email subject.
        :param str emailBody: The email subject.
        :return: SharingResult
        """

        result = ClientResult(SharingResult(self.context))
        file_result = ClientResult(str)

        role_values = {
            ExternalSharingSiteOption.View: "role:1073741826",
            ExternalSharingSiteOption.Edit: "role:1073741827",
        }

        def _property_resolved():
            file_result.value = self.get_property("EncodedAbsUrl")

        def _picker_value_resolved(picker_value):
            from office365.sharepoint.webs.web import Web
            result.value = Web.share_object(self.context, file_result.value, picker_value, role_values[shareOption],
                                            0,
                                            False, sendEmail, False, emailSubject, emailBody)

        self.ensure_property("EncodedAbsUrl", _property_resolved)
        params = ClientPeoplePickerQueryParameters(user_principal_name)
        ClientPeoplePickerWebServiceInterface.client_people_picker_resolve_user(self.context,
                                                                                params, _picker_value_resolved)
        return result.value

    def unshare(self):
        """
                Share a ListItem (file or folder facet)
        """
        result = ClientResult(SharingResult(self.context))

        def _property_resolved():
            abs_url = self.get_property("EncodedAbsUrl")
            from office365.sharepoint.webs.web import Web
            result.value = Web.unshare_object(self.context, abs_url)

        self.ensure_property("EncodedAbsUrl", _property_resolved)
        return result.value

    def get_sharing_information(self):
        result = ClientResult(ObjectSharingInformation(self.context))

        def _item_resolved():
            result.value = ObjectSharingInformation.get_list_item_sharing_information(
                self.context, self.parentList.properties["Id"], self.properties["Id"])

        self.ensure_property(["Id", "ParentList"], _item_resolved)
        return result.value

    def update(self):
        """Update the list item."""
        self.ensure_type_name(self.parentList)
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)

    def validate_update_list_item(self, form_values, new_document_update):
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
                                    "updateOverwriteVersion")
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the ListItem."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)

    def parse_and_set_field_value(self, fieldName, value):
        """Sets the value of the field (2) for the list item based on an implementation-specific transformation
           of the value..
           :param str fieldName: Specifies the field internal name.
           :param str value: Specifies the new value for the field (2).

        """
        payload = {
            "fieldName": fieldName,
            "value": value
        }
        qry = ServiceOperationQuery(self,
                                    "ParseAndSetFieldValue", None, payload, None, None)
        self.context.add_query(qry)

    @property
    def displayName(self):
        """Specifies the display name of the list item.

        :rtype: str or None
        """
        return self.properties.get("DisplayName", None)

    @property
    def parentList(self):
        """Get parent List"""
        if self.is_property_available("ParentList"):
            return self.properties["ParentList"]
        else:
            from office365.sharepoint.lists.list import List
            return List(self.context, ResourcePath("ParentList", self.resource_path))

    @property
    def file(self):
        """Get file"""
        if self.is_property_available("File"):
            return self.properties["File"]
        else:
            from office365.sharepoint.files.file import File
            return File(self.context, ResourcePath("File", self.resource_path))

    @property
    def folder(self):
        """Get folder"""
        if self.is_property_available("Folder"):
            return self.properties["Folder"]
        else:
            from office365.sharepoint.folders.folder import Folder
            return Folder(self.context, ResourcePath("Folder", self.resource_path))

    @property
    def attachmentFiles(self):
        """Specifies the collection of attachments that are associated with the list item.<62>"""
        if self.is_property_available('AttachmentFiles'):
            return self.properties["AttachmentFiles"]
        else:
            from office365.sharepoint.attachments.attachmentfile_collection import AttachmentFileCollection
            return AttachmentFileCollection(self.context,
                                            ResourcePath("AttachmentFiles", self.resource_path))

    @property
    def contentType(self):
        """Gets a value that specifies the content type of the list item."""
        from office365.sharepoint.contenttypes.content_type import ContentType
        return self.properties.get("ContentType",
                                   ContentType(self.context,
                                               ResourcePath("ContentType", self.resource_path))
                                   )

    @property
    def effectiveBasePermissions(self):
        """Gets a value that specifies the effective permissions on the list item that are assigned
           to the current user."""
        from office365.sharepoint.permissions.basePermissions import BasePermissions
        return self.properties.get("EffectiveBasePermissions",
                                   BasePermissions())

    @property
    def field_values(self):
        """Gets a collection of key/value pairs containing the names and values for the fields of the list item."""
        return self.properties.get("FieldValues", None)

    @property
    def comments_disabled(self):
        """
        :rtype: bool or None
        """
        return self.properties.get("CommentsDisabled", None)

    def set_property(self, name, value, persist_changes=True):
        super(ListItem, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Id" and self._parent_collection is not None:
                self._resource_path = ResourcePathServiceOperation(
                    "getItemById", [value], self._parent_collection.resource_path.parent)

    def ensure_type_name(self, target_list):
        """
        Determine metadata annotation for ListItem entity

        :param office365.sharepoint.lists.list.List target_list: List entity
        """

        def _init_item_type():
            self._entity_type_name = target_list.properties['ListItemEntityTypeFullName']

        if not self._entity_type_name:
            target_list.ensure_property("ListItemEntityTypeFullName", _init_item_type)

    def to_json(self):
        payload_orig = super(ListItem, self).to_json()
        payload = {}
        for k, v in payload_orig.items():
            if isinstance(v, FieldMultiLookupValue):
                collection = ClientValueCollection(int)
                [collection.add(lv.LookupId) for lv in v]
                payload["{name}Id".format(name=k)] = collection
            elif isinstance(v, FieldLookupValue):
                payload["{name}Id".format(name=k)] = v
            else:
                payload[k] = v
        return payload
