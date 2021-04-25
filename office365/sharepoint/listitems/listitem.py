from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.changes.change_collection import ChangeCollection
from office365.sharepoint.changes.change_query import ChangeQuery
from office365.sharepoint.comments.comment_collection import CommentCollection
from office365.sharepoint.fields.field_lookup_value import FieldLookupValue
from office365.sharepoint.fields.fieldMultiLookupValue import FieldMultiLookupValue
from office365.sharepoint.likes.likedByInformation import LikedByInformation
from office365.sharepoint.permissions.securable_object import SecurableObject
from office365.sharepoint.sharing.externalSharingSiteOption import ExternalSharingSiteOption
from office365.sharepoint.sharing.object_sharing_information import ObjectSharingInformation
from office365.sharepoint.sharing.sharing_result import SharingResult
from office365.sharepoint.ui.applicationpages.client_people_picker import (
    ClientPeoplePickerWebServiceInterface, ClientPeoplePickerQueryParameters
)


class ListItem(SecurableObject):
    """An individual entry within a SharePoint list. Each list item has a schema that maps to fields in the list
    that contains the item, depending on the content type of the item."""

    def get_wopi_frame_url(self, action):
        """
        Gets the full URL to the SharePoint frame page that initiates the SPWOPIAction object with the WOPI
            application associated with the list item.
        :param int action:
        """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "GetWOPIFrameUrl", [action], None, None, result)
        self.context.add_query(qry)
        return result

    def recycle(self):
        """Moves the listItem to the Recycle Bin and returns the identifier of the new Recycle Bin item."""

        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "Recycle", None, None, None, result)
        self.context.add_query(qry)
        return result

    def get_changes(self, query=None):
        """Returns the collection of changes from the change log that have occurred within the ListItem,
           based on the specified query.

        :param office365.sharepoint.changeQuery.ChangeQuery query: Specifies which changes to return
        """
        if query is None:
            query = ChangeQuery(item=True)
        changes = ChangeCollection(self.context)
        qry = ServiceOperationQuery(self, "getChanges", None, query, "query", changes)
        self.context.add_query(qry)
        return changes

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
        :rtype: SharingResult
        """

        result = ClientResult(self.context, SharingResult(self.context))
        file_result = ClientResult(self.context)

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
        Unshare a ListItem (file or folder facet)

        :rtype: SharingResult
        """
        result = ClientResult(self.context, SharingResult(self.context))

        def _property_resolved():
            abs_url = self.get_property("EncodedAbsUrl")
            from office365.sharepoint.webs.web import Web
            result.value = Web.unshare_object(self.context, abs_url)

        self.ensure_property("EncodedAbsUrl", _property_resolved)
        return result.value

    def get_sharing_information(self):
        """

        :rtype: ObjectSharingInformation
        """
        result = ClientResult(self.context, ObjectSharingInformation(self.context))

        def _item_resolved():
            result.value = ObjectSharingInformation.get_list_item_sharing_information(
                self.context, self.parent_list.properties["Id"], self.properties["Id"])

        self.ensure_properties(["Id", "ParentList"], _item_resolved)
        return result.value

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
        return self

    def system_update(self):
        """Update the list item."""
        qry = ServiceOperationQuery(self,
                                    "systemUpdate")
        self.context.add_query(qry)
        return self

    def update_overwrite_version(self):
        """Update the list item."""
        qry = ServiceOperationQuery(self,
                                    "updateOverwriteVersion")
        self.context.add_query(qry)
        return self

    def set_comments_disabled(self, value):
        """
        :type value: bool
        """
        qry = ServiceOperationQuery(self, "SetCommentsDisabled", [value])
        self.context.add_query(qry)
        return self

    def get_comments(self):
        comments = CommentCollection(self.context)
        qry = ServiceOperationQuery(self, "getComments", [], None, None, comments)
        self.context.add_query(qry)
        return comments

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
    def display_name(self):
        """Specifies the display name of the list item.

        :rtype: str or None
        """
        return self.properties.get("DisplayName", None)

    @property
    def parent_list(self):
        """Get parent List"""
        from office365.sharepoint.lists.list import List
        return self.properties.get("ParentList", List(self.context, ResourcePath("ParentList", self.resource_path)))

    @property
    def file(self):
        """Get file"""
        from office365.sharepoint.files.file import File
        return self.properties.get("File", File(self.context, ResourcePath("File", self.resource_path)))

    @property
    def folder(self):
        """Get folder"""
        from office365.sharepoint.folders.folder import Folder
        return self.properties.get("Folder", Folder(self.context, ResourcePath("Folder", self.resource_path)))

    @property
    def attachment_files(self):
        """Specifies the collection of attachments that are associated with the list item.<62>"""
        from office365.sharepoint.attachments.attachmentfile_collection import AttachmentFileCollection
        return self.properties.get("AttachmentFiles",
                                   AttachmentFileCollection(self.context,
                                                            ResourcePath("AttachmentFiles", self.resource_path)))

    @property
    def content_type(self):
        """Gets a value that specifies the content type of the list item."""
        from office365.sharepoint.contenttypes.content_type import ContentType
        return self.properties.get("ContentType", ContentType(self.context,
                                                              ResourcePath("ContentType", self.resource_path)))

    @property
    def effective_base_permissions(self):
        """Gets a value that specifies the effective permissions on the list item that are assigned
           to the current user."""
        from office365.sharepoint.permissions.base_permissions import BasePermissions
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

    @property
    def file_system_object_type(self):
        """
        Gets a value that specifies whether the list item is a file or a list folder.
        :rtype: str or None
        """
        return self.properties.get("FileSystemObjectType", None)

    @property
    def id(self):
        """
        Gets a value that specifies the list item identifier.
        :rtype: int
        """
        return self.properties.get("Id", None)

    @property
    def liked_by_information(self):
        """
        Gets a value that specifies the list item identifier.
        :rtype: int
        """
        return self.properties.get("LikedByInformation",
                                   LikedByInformation(self.context,
                                                      ResourcePath("likedByInformation", self.resource_path)))

    def get_property(self, name):
        if name == "ContentType":
            return self.content_type
        elif name == "ParentList":
            return self.parent_list
        elif name == "EffectiveBasePermissions":
            return self.effective_base_permissions
        elif name == "AttachmentFiles":
            return self.attachment_files
        elif name == "LikedByInformation":
            return self.liked_by_information
        else:
            return super(ListItem, self).get_property(name)

    def set_property(self, name, value, persist_changes=True):
        super(ListItem, self).set_property(name, value, persist_changes)

        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Id" and self._parent_collection is not None:
                self._resource_path = ResourcePathServiceOperation(
                    "getItemById", [value], self._parent_collection.resource_path.parent)
        return self

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
                payload["{name}Id".format(name=k)] = v.LookupId
            else:
                payload[k] = v
        return payload
