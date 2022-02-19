from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.changes.change_collection import ChangeCollection
from office365.sharepoint.changes.change_query import ChangeQuery
from office365.sharepoint.comments.comment_collection import CommentCollection
from office365.sharepoint.fields.field_lookup_value import FieldLookupValue
from office365.sharepoint.fields.fieldMultiLookupValue import FieldMultiLookupValue
from office365.sharepoint.likes.liked_by_information import LikedByInformation
from office365.sharepoint.listitems.form_update_value import ListItemFormUpdateValue
from office365.sharepoint.listitems.list_item_version import ListItemVersion
from office365.sharepoint.permissions.securable_object import SecurableObject
from office365.sharepoint.reputationmodel.reputation import Reputation
from office365.sharepoint.sharing.externalSharingSiteOption import ExternalSharingSiteOption
from office365.sharepoint.sharing.object_sharing_information import ObjectSharingInformation
from office365.sharepoint.sharing.sharing_result import SharingResult
from office365.sharepoint.taxonomy.taxonomy_field_value import TaxonomyFieldValueCollection
from office365.sharepoint.ui.applicationpages.client_people_picker import (
    ClientPeoplePickerWebServiceInterface, ClientPeoplePickerQueryParameters
)


class ListItem(SecurableObject):
    """An individual entry within a SharePoint list. Each list item has a schema that maps to fields in the list
    that contains the item, depending on the content type of the item."""

    def __init__(self, context, resource_path=None, parent_list=None):
        """

        :type context: office365.sharepoint.client_context.ClientContext
        :type resource_path: office365.runtime.client_path.ClientPath or None
        :type parent_list: office365.sharepoint.lists.list.List or None
        """
        super(ListItem, self).__init__(context, resource_path)
        if parent_list is not None:
            self.set_property("ParentList", parent_list, False)

    def set_rating(self, value):
        """
        Rates an item within the specified list. The return value is the average rating for the specified list item.

        :param int value: An integer value for the rating to be submitted.
            The rating value SHOULD be between 1 and 5; otherwise, the server SHOULD return an exception.
        """
        return_value = ClientResult(self.context)

        def _list_item_loaded():
            Reputation.set_rating(self.context, self.parent_list.id, self.id, value, return_value)
        self.parent_list.ensure_properties(["Id", "ParentList"], _list_item_loaded)
        return return_value

    def set_like(self, value):
        """
        Sets or unsets the like quality for the current user for an item within
           the specified list. The return value is the total number of likes for the specified list item.

        :param bool value: A Boolean value that indicates the operation being either like or unlike.
            A True value indicates like.
        """
        return_value = ClientResult(self.context)

        def _list_item_loaded():
            Reputation.set_like(self.context, self.parent_list.id, self.id, value, return_value)
        self.parent_list.ensure_properties(["Id", "ParentList"], _list_item_loaded)
        return return_value

    def get_wopi_frame_url(self, action):
        """
        Gets the full URL to the SharePoint frame page that initiates the SPWOPIAction object with the WOPI
            application associated with the list item.


        :param int action: Indicates which user action is indicated in the returned WOPIFrameUrl.
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
              share_option=ExternalSharingSiteOption.View,
              send_email=True, email_subject=None, email_body=None):
        """
        Share a ListItem (file or folder facet)

        :param str user_principal_name: User identifier
        :param ExternalSharingSiteOption share_option: The sharing type of permission to grant on the object.
        :param bool send_email: A flag to determine if an email notification SHOULD be sent (if email is configured).
        :param str email_subject: The email subject.
        :param str email_body: The email subject.
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
            result.value = Web.share_object(self.context, file_result.value, picker_value, role_values[share_option],
                                            0,
                                            False, send_email, False, email_subject, email_body)

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
        Retrieves information about the sharing state for a given list item.

        """
        return_type = ObjectSharingInformation(self.context)

        def _item_resolved():
            ObjectSharingInformation.get_list_item_sharing_information(
                self.context, self.parent_list.properties["Id"], self.properties["Id"], return_type=return_type)

        self.ensure_properties(["Id", "ParentList"], _item_resolved)
        return return_type

    def validate_update_list_item(self, form_values, new_document_update=False, checkin_comment=None):
        """Validates and sets the values of the specified collection of fields for the list item.

        :param dict form_values: Specifies a collection of field internal names and values for the given field
        :param dict new_document_update: Specifies whether the list item is a document being updated after upload.
        :param str checkin_comment: Check-in comment, if any. This parameter is only applicable when the list item
             is checked out.
        """
        normalized_form_values = [ListItemFormUpdateValue(k, v) for k, v in form_values.items()]
        payload = {
            "formValues": normalized_form_values,
            "bNewDocumentUpdate": new_document_update,
            "checkInComment": checkin_comment,
            "datesInUTC": True
        }
        result = ClientResult(self.context, ClientValueCollection(ListItemFormUpdateValue))
        qry = ServiceOperationQuery(self, "ValidateUpdateListItem", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def update(self):
        """
        Updates the item without creating another version of the item.
        Exceptions:
        - 2130575305 Microsoft.SharePoint.SPException List item was modified on the server in a way that prevents
            changes from being committed, as determined by the protocol server.
        -1 System.InvalidOperationException List does not support this operation.

        """
        self.ensure_type_name(self.parent_list)
        super(ListItem, self).update()
        return self

    def system_update(self):
        """Update the list item."""
        qry = ServiceOperationQuery(self, "SystemUpdate")
        self.context.add_query(qry)
        return self

    def update_overwrite_version(self):
        """Updates the item without creating another version of the item."""
        qry = ServiceOperationQuery(self, "UpdateOverwriteVersion")
        self.context.add_query(qry)
        return self

    def set_comments_disabled(self, value):
        """
        Sets the value of CommentsDisabled (section 3.2.5.87.1.1.8) for the item.

        :type value: bool
        """
        qry = ServiceOperationQuery(self, "SetCommentsDisabled", [value])
        self.context.add_query(qry)
        return self

    def get_comments(self):
        comments = CommentCollection(self.context)
        qry = ServiceOperationQuery(self, "GetComments", [], None, None, comments)
        self.context.add_query(qry)
        return comments

    def parse_and_set_field_value(self, field_name, value):
        """Sets the value of the field (2) for the list item based on an implementation-specific transformation
           of the value..
           :param str field_name: Specifies the field internal name.
           :param str value: Specifies the new value for the field (2).

        """
        payload = {
            "fieldName": field_name,
            "value": value
        }
        qry = ServiceOperationQuery(self, "ParseAndSetFieldValue", None, payload)
        self.context.add_query(qry)
        return self

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
        return self.properties.get("EffectiveBasePermissions", BasePermissions())

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
        :rtype: LikedByInformation
        """
        return self.properties.get("LikedByInformation",
                                   LikedByInformation(self.context,
                                                      ResourcePath("likedByInformation", self.resource_path)))

    @property
    def versions(self):
        """Gets the collection of item version objects that represent the versions of the item."""
        return self.properties.get('Versions',
                                   BaseEntityCollection(self.context, ListItemVersion,
                                                        ResourcePath("versions", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "AttachmentFiles": self.attachment_files,
                "ContentType": self.content_type,
                "EffectiveBasePermissions": self.effective_base_permissions,
                "LikedByInformation": self.liked_by_information,
                "ParentList": self.parent_list,
            }
            default_value = property_mapping.get(name, None)

        value = super(ListItem, self).get_property(name, default_value)
        if self.is_property_available(name[:-2]):
            lookup_value = super(ListItem, self).get_property(name[:-2], default_value)
            if isinstance(lookup_value, FieldMultiLookupValue):
                return ClientValueCollection(int, [v.LookupId for v in lookup_value])
            elif isinstance(lookup_value, FieldLookupValue):
                return lookup_value.LookupId
        return value

    def set_property(self, name, value, persist_changes=True):
        if persist_changes:
            if isinstance(value, TaxonomyFieldValueCollection):
                self._set_taxonomy_field_value(name, value)
            elif isinstance(value, FieldMultiLookupValue):
                collection = ClientValueCollection(int, [v.LookupId for v in value])
                super(ListItem, self).set_property("{name}Id".format(name=name), collection)
                super(ListItem, self).set_property(name, value, False)
            elif isinstance(value, FieldLookupValue):
                super(ListItem, self).set_property("{name}Id".format(name=name), value.LookupId)
                super(ListItem, self).set_property(name, value, False)
            else:
                super(ListItem, self).set_property(name, value, persist_changes)
        else:
            super(ListItem, self).set_property(name, value, persist_changes)

        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Id" and self._parent_collection is not None:
                self._resource_path = ServiceOperationPath(
                    "getItemById", [value], self._parent_collection.resource_path.parent)
        return self

    def _set_taxonomy_field_value(self, name, value):
        tax_field = self.parent_list.fields.get_by_internal_name_or_title(name)

        def _tax_field_loaded():
            tax_text_field = self.parent_list.fields.get_by_id(tax_field.properties["TextField"])

            def _tax_text_field_loaded():
                self.set_property(tax_text_field.properties["StaticName"], str(value))

            tax_text_field.ensure_property("StaticName", _tax_text_field_loaded)

        tax_field.ensure_property("TextField", _tax_field_loaded)

    def ensure_type_name(self, target_list):
        """
        Determine metadata annotation for ListItem entity

        :param office365.sharepoint.lists.list.List target_list: List resource
        """

        def _init_item_type():
            self._entity_type_name = target_list.properties['ListItemEntityTypeFullName']

        if not self._entity_type_name:
            target_list.ensure_property("ListItemEntityTypeFullName", _init_item_type)
