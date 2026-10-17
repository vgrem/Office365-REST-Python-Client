from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Dict, Union
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.converters.scalars import iso_z
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.paths.v3.entity import EntityPath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.attachments.collection import AttachmentCollection
from office365.sharepoint.changes.collection import ChangeCollection
from office365.sharepoint.changes.query import ChangeQuery
from office365.sharepoint.comments.collection import CommentCollection
from office365.sharepoint.fields.geolocation_value import FieldGeolocationValue
from office365.sharepoint.fields.image_value import ImageFieldValue
from office365.sharepoint.fields.lookup_value import FieldLookupValue
from office365.sharepoint.fields.multi_choice_value import FieldMultiChoiceValue
from office365.sharepoint.fields.multi_lookup_value import FieldMultiLookupValue
from office365.sharepoint.fields.multi_user_value import FieldMultiUserValue
from office365.sharepoint.fields.string_values import FieldStringValues
from office365.sharepoint.fields.url_value import FieldUrlValue
from office365.sharepoint.files.system_object_type import FileSystemObjectType
from office365.sharepoint.likes.liked_by_information import LikedByInformation
from office365.sharepoint.listitems.compliance_info import ListItemComplianceInfo
from office365.sharepoint.listitems.form_update_value import ListItemFormUpdateValue
from office365.sharepoint.listitems.update_parameters import ListItemUpdateParameters
from office365.sharepoint.listitems.versions.collection import ListItemVersionCollection
from office365.sharepoint.lists.templates.type import ListTemplateType
from office365.sharepoint.permissions.securable_object import SecurableObject
from office365.sharepoint.policy.dlp_policy_tip import DlpPolicyTip
from office365.sharepoint.reputationmodel.reputation import Reputation
from office365.sharepoint.sharing.external_site_option import ExternalSharingSiteOption
from office365.sharepoint.sharing.links.share_request import ShareLinkRequest
from office365.sharepoint.sharing.links.share_response import ShareLinkResponse
from office365.sharepoint.sharing.links.share_settings import ShareLinkSettings
from office365.sharepoint.sharing.object_sharing_information import (
    ObjectSharingInformation,
)
from office365.sharepoint.sharing.result import SharingResult
from office365.sharepoint.taxonomy.field_value_col import TaxonomyFieldValueCollection
from office365.sharepoint.types.wopi_action import SPWOPIAction
from office365.sharepoint.ui.applicationpages.peoplepicker.web_service_interface import (
    ClientPeoplePickerWebServiceInterface,
)

if TYPE_CHECKING:
    import datetime
    from typing import Optional

    from office365.sharepoint.approvals.mediaserviceupdateparameters import (
        MediaServiceUpdateParameters,
    )
    from office365.sharepoint.contenttypes.content_type import ContentType
    from office365.sharepoint.files.file import File
    from office365.sharepoint.folders.folder import Folder
    from office365.sharepoint.listitems.delete_parameters import (
        ListItemDeleteParameters,
    )
    from office365.sharepoint.listitems.updateresults import ListItemUpdateResults
    from office365.sharepoint.lists.list import List
    from office365.sharepoint.permissions.base_permissions import BasePermissions
    from office365.sharepoint.webs.spimageitem import SPImageItem
    from office365.sharepoint.workflow.labelaccesscontroldata import (
        LabelAccessControlData,
    )


class ListItem(SecurableObject):
    """An individual entry within a SharePoint list. Each list item has a schema that maps to fields in the list
    that contains the item, depending on the content type of the item."""

    def __init__(self, context, resource_path=None, parent_list=None):
        """Args:
        context (office365.sharepoint.client_context.ClientContext):
        resource_path (office365.runtime.paths.resource_path.ResourcePath or None):
        parent_list (office365.sharepoint.lists.list.List or None):
        """
        super().__init__(context, resource_path)
        if parent_list is not None:
            self.set_property("ParentList", parent_list, False)

    def archive(self) -> ClientResult[str]:
        """Archives the list item."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "Archive", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def lock_record_item(self) -> ClientResult[int]:
        """
        Locks a record item to prevent modifications.

        Returns:
            ClientResult[int]: Result containing status or identifier of the operation

        Remarks:
            Locking a record item typically prevents any modifications to ensure
            the integrity of records for compliance and legal purposes.
        """
        list_folder = self.parent_list.root_folder
        return_type = ClientResult(self.context, int())
        from office365.sharepoint.compliance.store_proxy import SPPolicyStoreProxy

        def _lock_record_item():
            assert list_folder.server_relative_url is not None
            assert self.id is not None
            SPPolicyStoreProxy.lock_record_item(
                self.context,
                list_folder.server_relative_url,
                self.id,
                return_type=return_type,
            )

        list_folder.ensure_property("ServerRelativeUrl").after_execute(lambda _: _lock_record_item())
        return return_type

    def share_link(
        self,
        link_kind: int,
        expiration: Union[None, datetime.datetime] = None,
        role: Union[None, int] = None,
        password: Union[None, str] = None,
        share_id: Union[None, str] = None,
    ) -> ClientResult[ShareLinkResponse]:
        """Creates a tokenized sharing link for a list item based on the specified parameters and optionally
        sends an email to the people that are listed in the specified parameters.

        Args:
            link_kind: The kind of the tokenized sharing link to be created/updated or retrieved.
            expiration: A date/time string for which the format conforms to the ISO 8601:2004(E) complete representation
                for calendar date and time of day and which represents the time and date of expiry for the tokenized
                sharing link. Both the minutes and hour value MUST be specified for the difference between the local and
                UTC time. Midnight is represented as 00:00:00. A null value indicates no expiry. This value is only
                applicable to tokenized sharing links that are anonymous access links.
            role: The role to be used for the tokenized sharing link. This is required for Flexible links and ignored
                for all other kinds.
            password: Optional password value to apply to the tokenized sharing link, if it can support password
                protection.
            share_id: Unique identifier of an existing tokenized sharing link to retrieve and update. When omitted
                the server retrieves a matching link or creates a new one.
        """
        return_type = ClientResult(self.context, ShareLinkResponse())
        request = ShareLinkRequest(
            settings=ShareLinkSettings(
                linkKind=link_kind,
                expiration=iso_z(expiration),
                role=role,
                password=password,
                shareId=share_id,
            )
        )
        if password:
            assert request.settings is not None
            request.settings.allowAnonymousAccess = True
            request.settings.updatePassword = True

        payload = {"request": request}
        qry = ServiceOperationQuery(self, "ShareLink", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def unshare_link(self, link_kind: int, share_id: Optional[str] = None) -> Self:
        """Removes the specified tokenized sharing link of the list item.

        Args:
            link_kind (int): This optional value specifies the globally unique identifier (GUID) of the tokenized
                sharing link that is intended to be removed.
            share_id (str or None): The kind of tokenized sharing link that is intended to be removed.
        """
        payload = {"linkKind": link_kind, "shareId": share_id}
        qry = ServiceOperationQuery(self, "UnshareLink", None, payload)
        self.context.add_query(qry)
        return self

    def delete_link_by_kind(self, link_kind):
        """Removes the specified tokenized sharing link of the list item

        Args:
            link_kind (int): The kind of tokenized sharing link that is intended to be removed.
                This MUST be set to one of the following values: OrganizationView (section 3.2.5.315.1.3)
                    OrganizationEdit (section 3.2.5.315.1.4) AnonymousView (section 3.2.5.315.1.5) AnonymousEdit
                    (section 3.2.5.315.1.6)
        """
        payload = {"linkKind": link_kind}
        qry = ServiceOperationQuery(self, "DeleteLinkByKind", None, payload)
        self.context.add_query(qry)
        return self

    def set_choice_field_value(self, field_name: str, field_value: str | list[str]) -> Self:
        """Sets the value of a Choice or MultiChoice field and persists the change.

        Args:
            field_name: The internal name of the choice field.
            field_value: The value to set — a plain string for single-choice
                fields, or a list of strings for multi-choice fields
                (e.g. ``["In Progress", "Completed"]``).
        """
        actual_value = field_value
        if isinstance(actual_value, list):
            actual_value = FieldMultiChoiceValue(actual_value)
        self.set_property(field_name, actual_value).update()
        return self

    def set_url_field_value(self, field_name: str, url: str, description: str | None = None) -> Self:
        """Sets the value of a URL (hyperlink) field and persists the change.

        Args:
            field_name: The internal name of the URL field.
            url: The URL value (e.g. ``"https://example.com"``).
            description: Optional display text for the link.
        """
        self.set_property(field_name, FieldUrlValue(url, Description=description)).update()
        return self

    def set_geo_field_value(self, field_name: str, latitude: float, longitude: float) -> Self:
        """Sets the value of a Geolocation field and persists the change.

        Args:
            field_name: The internal name of the geolocation field.
            latitude: The latitude value.
            longitude: The longitude value.
        """
        self.set_property(field_name, FieldGeolocationValue(latitude, longitude)).update()
        return self

    def set_multi_lookup_field_value(self, field_name: str, lookup_ids: list[int]) -> Self:
        """Sets the value of a multi-lookup field and persists the change.

        Args:
            field_name: The internal name of the lookup field.
            lookup_ids: The list of lookup item IDs (e.g. ``[1, 2, 3]``).
        """
        collection = FieldMultiLookupValue()
        for lid in lookup_ids:
            collection.add(FieldLookupValue(LookupId=lid))
        self.set_property(field_name, collection).update()
        return self

    def set_lookup_field_value(self, field_name: str, lookup_id: int) -> Self:
        """Sets the value of a single-value lookup field and persists the change.

        Args:
            field_name: The internal name of the lookup field.
            lookup_id: The lookup item ID.
        """
        self.set_property(field_name, FieldLookupValue(LookupId=lookup_id)).update()
        return self

    def set_rating(self, value: int) -> ClientResult[float]:
        """Rates an item within the specified list. The return value is the average rating for the specified list item.

        Args:
            value (int): An integer value for the rating to be submitted.
                The rating value SHOULD be between 1 and 5; otherwise, the server SHOULD return an exception.
        """
        return_value = ClientResult[float](self.context)

        def _set_rating():
            assert self.parent_list.id is not None
            assert self.id is not None
            Reputation.set_rating(self.context, self.parent_list.id, self.id, value, return_value)

        self.parent_list.ensure_properties(["Id", "ParentList"]).after_execute(lambda _: _set_rating())
        return return_value

    def set_like(self, value: bool) -> ClientResult[int]:
        """Sets or unsets the like quality for the current user for an item within
        the specified list. The return value is the total number of likes for the specified list item.

        Args:
            value (bool): A Boolean value that indicates the operation being either like or unlike.
                A True value indicates like.
        """
        return_value = ClientResult(self.context)

        def _list_item_loaded():
            assert self.parent_list.id is not None
            assert self.id is not None
            Reputation.set_like(self.context, self.parent_list.id, self.id, value, return_value)

        self.parent_list.ensure_properties(["Id", "ParentList"]).after_execute(lambda _: _list_item_loaded())
        return return_value

    def get_wopi_frame_url(self, action: SPWOPIAction) -> ClientResult[str]:
        """Gets the full URL to the SharePoint frame page that initiates the SPWOPIAction object with the WOPI
        application associated with the list item.

        Args:
            action (int): Indicates which user action is indicated in the returned WOPIFrameUrl.
        """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "GetWOPIFrameUrl", [action.value], None, None, result)
        self.context.add_query(qry)
        return result

    def recycle(self, ignore_missing: bool = False) -> ClientResult[str]:
        """Moves the listItem to the Recycle Bin and returns the identifier of the new Recycle Bin item.

        Args:
            ignore_missing (bool): When True, recycling an item that no longer
                exists (HTTP 404) succeeds instead of raising.
        """

        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "Recycle", None, None, None, result)
        self.context.add_query(qry)
        self._tolerate_missing(ignore_missing)
        return result

    def get_changes(self, query=None) -> ChangeCollection:
        """Returns the collection of changes from the change log that have occurred within the ListItem,
        based on the specified query.

        Args:
            query (office365.sharepoint.changeQuery.ChangeQuery): Specifies which changes to return
        """
        if query is None:
            query = ChangeQuery(Item=True)
        return_type = ChangeCollection(self.context)
        payload = {"query": query}
        qry = ServiceOperationQuery(self, "getChanges", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def share(
        self,
        user_principal_name: str,
        share_option=ExternalSharingSiteOption.View,
        send_email: bool = True,
        email_subject: Optional[str] = None,
        email_body: Optional[str] = None,
    ) -> SharingResult:
        """Share a ListItem (file or folder facet)

        Args:
            user_principal_name (str): User identifier
            share_option (ExternalSharingSiteOption): The sharing type of permission to grant on the object.
            send_email (bool): A flag to determine if an email notification SHOULD be sent (if email is configured).
            email_subject (str): The email subject.
            email_body (str): The email subject.
        """

        return_type = SharingResult(self.context)
        role_values = {
            ExternalSharingSiteOption.View: "role:1073741826",
            ExternalSharingSiteOption.Edit: "role:1073741827",
        }

        def _picker_value_resolved(picker_result: ClientResult) -> None:
            abs_url = self.encoded_abs_url
            assert abs_url is not None
            picker_value = f"[{picker_result.value}]"
            from office365.sharepoint.webs.web import Web

            Web.share_object(
                self.context,
                abs_url,
                picker_value,
                role_values[share_option],
                0,
                False,
                send_email,
                False,
                email_subject,
                email_body,
                return_type=return_type,
            )

        def _url_resolved():
            ClientPeoplePickerWebServiceInterface.client_people_picker_resolve_user(
                self.context, user_principal_name
            ).after_execute(_picker_value_resolved)

        self.ensure_property("EncodedAbsUrl").after_execute(lambda _: _url_resolved())
        return return_type

    def unshare(self) -> SharingResult:
        """Unshare a ListItem (file or folder facet)"""
        return_type = SharingResult(self.context)

        def _property_resolved():
            abs_url = self.encoded_abs_url
            assert abs_url is not None
            from office365.sharepoint.webs.web import Web

            Web.unshare_object(self.context, abs_url, return_type=return_type)

        self.ensure_property("EncodedAbsUrl").after_execute(lambda _: _property_resolved())
        return return_type

    def get_sharing_information(self) -> ObjectSharingInformation:
        """
        Retrieves information about the sharing state for a given list item.
        """
        return_type = ObjectSharingInformation(self.context)

        def _item_resolved():
            assert self.parent_list.id is not None
            assert self.id is not None
            ObjectSharingInformation.get_list_item_sharing_information(
                self.context, self.parent_list.id, self.id, return_type=return_type
            )

        self.ensure_properties(["Id", "ParentList"]).after_execute(lambda _: _item_resolved())
        return return_type

    def validate_update_list_item(
        self,
        form_values: Dict,
        new_document_update: bool = False,
        checkin_comment: Optional[str] = None,
        dates_in_utc: Optional[bool] = None,
    ) -> ClientResult[ClientValueCollection[ListItemFormUpdateValue]]:
        """Validates and sets the values of the specified collection of fields for the list item.

        Args:
            form_values (dict): Specifies a collection of field internal names and values for the given field
            new_document_update (bool): Specifies whether the list item is a document being updated after upload.
            checkin_comment (str): Check-in comment, if any.
                This parameter is only applicable when the list item is checked out.
            dates_in_utc (bool or None):
        """
        payload = {
            "formValues": [ListItemFormUpdateValue(k, v) for k, v in form_values.items()],
            "bNewDocumentUpdate": new_document_update,
            "checkInComment": checkin_comment,
            "datesInUTC": dates_in_utc,
        }
        return_type = ClientResult(self.context, ClientValueCollection(ListItemFormUpdateValue))
        qry = ServiceOperationQuery(self, "ValidateUpdateListItem", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def update(self) -> Self:  # type: ignore[override]
        """
        Updates the item without creating another version of the item.
        Exceptions:
        - 2130575305 Microsoft.SharePoint.SPException List item was modified on the server in a way that prevents
            changes from being committed, as determined by the protocol server.
        -1 System.InvalidOperationException List does not support this operation.

        """
        self.ensure_type_name(self.parent_list)
        super().update()
        return self

    def update_ex(self, bypass_quota_check: Optional[bool] = None, bypass_shared_lock: Optional[bool] = None):
        """Args:
        bypass_quota_check (bool):
        bypass_shared_lock (bool):
        """
        payload = {"parameters": ListItemUpdateParameters(bypass_quota_check, bypass_shared_lock)}
        qry = ServiceOperationQuery(self, "UpdateEx", None, payload)
        self.context.add_query(qry)
        return self

    def system_update(self):
        """Update the list item."""

        sys_metadata = ["EditorId", "Modified"]

        def _after_system_update(
            result: ClientResult[ClientValueCollection[ListItemFormUpdateValue]],
        ) -> None:
            has_any_error = any(item.HasException for item in result.value)  # type: ignore[attr-defined]
            if has_any_error:
                raise ValueError("Update ListItem failed")

        def _system_update():
            from office365.sharepoint.fields.user_value import FieldUserValue

            form_values = self.persistable_properties
            for n in sys_metadata:
                if n == "Id":
                    pass
                elif n.endswith("Id"):
                    user_id = self.get_property(n)
                    assert isinstance(user_id, int)
                    user = self.context.web.site_users.get_by_id(str(user_id))
                    form_values[n[:-2]] = FieldUserValue.from_user(user)
                else:
                    form_values[n] = self.get_property(n)

            self.validate_update_list_item(
                form_values=form_values,
                dates_in_utc=True,
                new_document_update=True,
            ).after_execute(_after_system_update)

        def _list_loaded():
            if self.parent_list.base_template == ListTemplateType.DocumentLibrary.value:
                self.ensure_properties(sys_metadata).after_execute(lambda _: _system_update())
            else:
                next_qry = ServiceOperationQuery(self, "SystemUpdate")
                self.context.add_query(next_qry)

        self.parent_list.ensure_properties(["BaseTemplate"]).after_execute(lambda _: _list_loaded())
        return self

    def update_overwrite_version(self) -> ListItem:
        """Updates the item without creating another version of the item."""
        qry = ServiceOperationQuery(self, "UpdateOverwriteVersion")
        self.context.add_query(qry)
        return self

    def set_comments_disabled(self, value: bool) -> Self:
        """Sets the value of CommentsDisabled for the item.

        Args:
            value (bool): Indicates whether comments for this item are disabled or not.
        """
        qry = ServiceOperationQuery(self, "SetCommentsDisabled", [value])
        self.context.add_query(qry)
        return self

    def set_compliance_tag_with_hold(self, compliance_tag: str) -> Self:
        """Sets a compliance tag with a hold

        Args:
            compliance_tag (str): The applying label (tag) to the list item
        """
        payload = {"complianceTag": compliance_tag}
        qry = ServiceOperationQuery(self, "SetComplianceTagWithHold", None, payload)
        self.context.add_query(qry)
        return self

    def get_comments(self) -> CommentCollection:
        """Retrieve ListItem comments"""
        return_type = CommentCollection(self.context, ServiceOperationPath("GetComments", [], self.resource_path))
        qry = ServiceOperationQuery(self, "GetComments", [], None, None, return_type)

        def _create_request(request: RequestOptions) -> None:
            request.method = HttpMethod.Get

        self.context.add_query(qry).before_execute(_create_request)
        return return_type

    def override_policy_tip(self, user_action, justification):
        """Overrides the policy tip on this list item.

        Args:
            user_action (int): The user action to take.
            justification (str): The reason why the override is being done.
        """
        return_type = ClientResult(self.context, int())
        payload = {"userAction": user_action, "justification": justification}
        qry = ServiceOperationQuery(self, "OverridePolicyTip", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def parse_and_set_field_value(self, field_name: str, value: str) -> Self:
        """Sets the value of the field (2) for the list item based on an implementation-specific transformation
        of the value.

        Args:
            field_name (str): Specifies the field internal name.
            value (str): Specifies the new value for the field (2).
        """
        payload = {"fieldName": field_name, "value": value}
        qry = ServiceOperationQuery(self, "ParseAndSetFieldValue", None, payload)
        self.context.add_query(qry)
        return self

    @property
    def display_name(self) -> Optional[str]:
        """Specifies the display name of the list item."""
        return self.properties.get("DisplayName", None)

    @property
    def parent_list(self) -> List:
        """Get parent List"""
        from office365.sharepoint.lists.list import List

        return self.properties.setdefault(
            "ParentList",
            List(self.context, ResourcePath("ParentList", self.resource_path)),
        )

    @property
    def file(self) -> File:
        """Get file"""
        from office365.sharepoint.files.file import File

        return self.properties.get("File", File(self.context, ResourcePath("File", self.resource_path)))

    @property
    def folder(self) -> Folder:
        """Get folder"""
        from office365.sharepoint.folders.folder import Folder

        return self.properties.get("Folder", Folder(self.context, ResourcePath("Folder", self.resource_path)))

    @property
    def attachment_files(self) -> AttachmentCollection:
        """Specifies the collection of attachments that are associated with the list item.<62>"""
        from office365.sharepoint.attachments.collection import (
            AttachmentCollection,  # noqa
        )

        return self.properties.get(
            "AttachmentFiles",
            AttachmentCollection(self.context, ResourcePath("AttachmentFiles", self.resource_path), self),
        )

    @property
    def content_type(self) -> ContentType:
        """Gets a value that specifies the content type of the list item."""
        from office365.sharepoint.contenttypes.content_type import ContentType

        return self.properties.get(
            "ContentType",
            ContentType(self.context, ResourcePath("ContentType", self.resource_path)),
        )

    @property
    def effective_base_permissions(self) -> BasePermissions:
        """Gets a value that specifies the effective permissions on the list item that are assigned
        to the current user."""
        from office365.sharepoint.permissions.base_permissions import BasePermissions

        return self.properties.get("EffectiveBasePermissions", BasePermissions())

    @property
    def effective_base_permissions_for_ui(self) -> BasePermissions:
        """Specifies the effective base permissions for the current user, as they SHOULD be displayed in the user
        interface (UI). If the list is not in read-only UI mode, the value of EffectiveBasePermissionsForUI
        MUST be the same as the value of EffectiveBasePermissions (section 3.2.5.87.1.1.2).
        If the list is in read-only UI mode, the value of EffectiveBasePermissionsForUI MUST be a subset of the
        value of EffectiveBasePermissions."""
        from office365.sharepoint.permissions.base_permissions import BasePermissions

        return self.properties.get("EffectiveBasePermissionsForUI", BasePermissions())

    @property
    def field_values(self) -> Optional[dict]:
        """Gets a collection of key/value pairs containing the names and values for the fields of the list item."""
        return self.properties.get("FieldValues", None)

    @property
    def comments_disabled(self) -> Optional[bool]:
        """Indicates whether comments for this item are disabled or not."""
        return self.properties.get("CommentsDisabled", None)

    @property
    def file_system_object_type(self) -> Optional[FileSystemObjectType]:
        """Gets a value that specifies whether the list item is a file or a list folder"""
        return self.properties.get("FileSystemObjectType", FileSystemObjectType.Invalid)

    @property
    def icon_overlay(self) -> Optional[str]:
        """This is an overlay icon for the item. If the parent list of the item does not already have the IconOverlay
        field and The user setting the property does not have rights to add the field to the list then the property
        will not be set for the item."""
        return self.properties.get("IconOverlay", None)

    @property
    def id(self) -> Optional[int]:
        """Gets a value that specifies the list item identifier."""
        return self.properties.get("Id", None)

    @property
    def server_redirected_embed_uri(self) -> Optional[str]:
        """Returns the path for previewing a document in the browser, often in an interactive way, if
        that feature exists."""
        return self.properties.get("ServerRedirectedEmbedUri", None)

    @property
    def server_redirected_embed_url(self) -> Optional[str]:
        """Returns the URL for previewing a document in the browser, often in an interactive way, if that feature
        exists. This is currently used in the hovering panel of search results and document library.
        """
        return self.properties.get("ServerRedirectedEmbedUri", None)

    @property
    def client_title(self) -> Optional[str]:
        """ """
        return self.properties.get("Client_Title", None)

    @property
    def compliance_info(self) -> ListItemComplianceInfo:
        return self.properties.get("ComplianceInfo", ListItemComplianceInfo())

    @property
    def comments_disabled_scope(self) -> Optional[str]:
        """Indicates at what scope comments are disabled."""
        return self.properties.get("CommentsDisabledScope", None)

    @property
    def get_dlp_policy_tip(self) -> DlpPolicyTip:
        """Gets the Data Loss Protection policy tip notification for this item."""
        return self.properties.get(
            "GetDlpPolicyTip",
            DlpPolicyTip(self.context, ResourcePath("GetDlpPolicyTip", self.resource_path)),
        )

    @property
    def field_values_as_html(self) -> FieldStringValues:
        """Specifies the values for the list item as Hypertext Markup Language (HTML)."""
        return self.properties.get(
            "FieldValuesAsHtml",
            FieldStringValues(self.context, ResourcePath("FieldValuesAsHtml", self.resource_path)),
        )

    @property
    def liked_by_information(self) -> LikedByInformation:
        """Gets a value that specifies the list item identifier."""
        return self.properties.get(
            "LikedByInformation",
            LikedByInformation(self.context, ResourcePath("likedByInformation", self.resource_path)),
        )

    @property
    def versions(self) -> ListItemVersionCollection:
        """Gets the collection of item version objects that represent the versions of the item."""
        return self.properties.get(
            "Versions",
            ListItemVersionCollection(self.context, ResourcePath("versions", self.resource_path)),
        )

    @property
    def doc_id(self) -> Optional[str]:
        """Document ID fora document"""
        return self.properties.get("OData__dlc_DocId", None)

    @property
    def encoded_abs_url(self) -> Optional[str]:
        """Gets the EncodedAbsUrl property"""
        return self.properties.get("EncodedAbsUrl", None)

    @property
    def doc_id_url(self) -> Optional[FieldUrlValue]:
        """Document ID fora document"""
        return self.properties.get("OData__dlc_DocIdUrl", FieldUrlValue())

    def get_property(self, name, default_value=None) -> Any:
        if default_value is None:
            property_mapping = {
                "AttachmentFiles": self.attachment_files,
                "ContentType": self.content_type,
                "ComplianceInfo": self.compliance_info,
                "OData__dlc_DocIdUrl": self.doc_id_url,
                "EffectiveBasePermissions": self.effective_base_permissions,
                "EffectiveBasePermissionsForUI": self.effective_base_permissions_for_ui,
                "GetDlpPolicyTip": self.get_dlp_policy_tip,
                "FieldValuesAsHtml": self.field_values_as_html,
                "FileSystemObjectType": self.file_system_object_type,
                "LikedByInformation": self.liked_by_information,
                "ParentList": self.parent_list,
            }
            default_value = property_mapping.get(name, None)

        value = super().get_property(name, default_value)
        if self.is_property_available(name[:-2]):
            lookup_value = super().get_property(name[:-2], default_value)
            if isinstance(lookup_value, (FieldMultiLookupValue, FieldMultiUserValue)):
                return ClientValueCollection(int, [v.LookupId for v in lookup_value])
            elif isinstance(lookup_value, FieldLookupValue):
                return lookup_value.LookupId
        return value

    def set_property(self, name, value, persist_changes=True):
        if persist_changes:
            if isinstance(value, TaxonomyFieldValueCollection):
                self._set_taxonomy_field_value(name, value)
            elif isinstance(value, ImageFieldValue):
                super().set_property(name, json.dumps(value.to_json()), persist_changes)
            elif isinstance(value, (FieldMultiLookupValue, FieldMultiUserValue)):
                collection = ClientValueCollection(int, [v.LookupId for v in value])
                super().set_property(f"{name}Id", collection)
                super().set_property(name, value, False)
            elif isinstance(value, FieldLookupValue):
                super().set_property(f"{name}Id", value.LookupId)
                super().set_property(name, value, False)
            else:
                super().set_property(name, value, persist_changes)
        else:
            super().set_property(name, value, persist_changes)

        # fallback: create a new resource path
        if name == "Id":
            if self._resource_path is None and self.parent_collection is not None:
                self._resource_path = EntityPath(value, self.parent_collection.resource_path)  # type: ignore[arg-type]
            else:
                self._resource_path.set_segment(value)  # type: ignore[arg-type]
        return self

    def _set_taxonomy_field_value(self, name: str, value: TaxonomyFieldValueCollection) -> None:
        """Sets a multi-value taxonomy column.

        A taxonomy column keeps its value in a hidden note companion column, and
        the collection must be written there as a ``WssId;#Label|TermGuid`` string.
        The companion's *item* property is its ``EntityPropertyName`` (==
        ``InternalName``) — not the field's ``StaticName``, which for a
        library-created column is a random token (writing it fails with "The
        property ... does not exist on type"). Because ``update()``/``create()``
        snapshot the item properties when they are called, the companion name is
        resolved synchronously here; a deferred lookup would set the property after
        the payload was already built and silently drop the value.

        Args:
            name (str): Taxonomy field name
            value (TaxonomyFieldValueCollection): Taxonomy field value
        """
        if self.parent_list is None:
            return
        try:
            tax_field = (
                self.parent_list.fields.get_by_internal_name_or_title(name).select(["TextField"]).get().execute_query()
            )
            text_field_id = tax_field.properties.get("TextField")
            if not text_field_id:
                return
            text_field = (
                self.parent_list.fields.get_by_id(text_field_id)
                .select(["EntityPropertyName", "InternalName", "StaticName"])
                .get()
                .execute_query()
            )
        except Exception:  # noqa: BLE001 — an unresolvable companion leaves the column unset
            return
        properties = text_field.properties
        note_name = (
            properties.get("EntityPropertyName") or properties.get("InternalName") or properties.get("StaticName")
        )
        if note_name:
            self.set_property(note_name, str(value))

    def ensure_type_name(self, target_list) -> Self:
        """Determine the metadata type annotation for this list item.

        Adopts the target list's ``ListItemEntityTypeFullName`` once it is available.
        When the list has not resolved it yet, a deferred barrier is queued right after
        the read, so the annotation is set before any query built afterwards executes
        -- including inside ``execute_batch``.

        Args:
            target_list (office365.sharepoint.lists.list.List): List resource
        """
        if self._entity_type_name is None:
            from office365.runtime.queries.deferred import DeferredOperationQuery

            def _list_loaded():
                self._entity_type_name = target_list.properties["ListItemEntityTypeFullName"]

            target_list.ensure_property("ListItemEntityTypeFullName").after_execute(lambda _: _list_loaded())
            target_list.context.add_query(DeferredOperationQuery(target_list.context))
        return self

    @property
    def field_values_as_text(self) -> FieldStringValues:
        """Gets the FieldValuesAsText property"""
        from office365.sharepoint.fields.string_values import FieldStringValues

        return self.properties.get(
            "FieldValuesAsText", FieldStringValues(self.context, ResourcePath("FieldValuesAsText", self.resource_path))
        )

    @property
    def field_values_for_edit(self) -> FieldStringValues:
        """Gets the FieldValuesForEdit property"""
        from office365.sharepoint.fields.string_values import FieldStringValues

        return self.properties.get(
            "FieldValuesForEdit", FieldStringValues(self.context, ResourcePath("FieldValuesForEdit", self.resource_path))
        )

    def add_thumbnail_field_data(
        self, image_stream: bytes, image_name: str, field_internal_name: str, lock_id: str
    ) -> ClientResult[SPImageItem]:
        """AddThumbnailFieldData operation.

        Args:
            image_stream (bytes):
                imageStream parameter
            image_name (str):
                imageName parameter
            field_internal_name (str):
                fieldInternalName parameter
            lock_id (str):
                lockId parameter
        """
        from office365.sharepoint.webs.spimageitem import SPImageItem

        return_type = ClientResult(self.context, SPImageItem())
        qry = ServiceOperationQuery(
            self,
            "AddThumbnailFieldData",
            None,
            {
                "imageStream": image_stream,
                "imageName": image_name,
                "fieldInternalName": field_internal_name,
                "lockId": lock_id,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def delete_with_parameters(self, parameters: ListItemDeleteParameters) -> Self:
        """DeleteWithParameters operation.

        Args:
            parameters (ListItemDeleteParameters):
                parameters parameter
        """
        qry = ServiceOperationQuery(self, "DeleteWithParameters", None, {"parameters": parameters}, None, None)
        self.context.add_query(qry)
        return self

    def do_entities_have_access_to_label(
        self, people_picker_input: str
    ) -> ClientResult[ClientValueCollection[LabelAccessControlData]]:
        """DoEntitiesHaveAccessToLabel operation.

        Args:
            people_picker_input (str):
                peoplePickerInput parameter
        """
        from office365.sharepoint.workflow.labelaccesscontroldata import (
            LabelAccessControlData,
        )

        return_type = ClientResult(self.context, ClientValueCollection[LabelAccessControlData]())
        qry = ServiceOperationQuery(
            self, "DoEntitiesHaveAccessToLabel", None, {"peoplePickerInput": people_picker_input}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def folder_archive_progress(self) -> ClientResult[str]:
        """FolderArchiveProgress operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "FolderArchiveProgress", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def folder_unarchive_progress(self) -> ClientResult[str]:
        """FolderUnarchiveProgress operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "FolderUnarchiveProgress", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def media_service_update(self, parameters: MediaServiceUpdateParameters) -> Self:
        """MediaServiceUpdate operation.

        Args:
            parameters (MediaServiceUpdateParameters):
                parameters parameter
        """
        qry = ServiceOperationQuery(self, "MediaServiceUpdate", None, {"parameters": parameters}, None, None)
        self.context.add_query(qry)
        return self

    def media_service_update_v2(self, parameters: MediaServiceUpdateParameters, event_firing_enabled: bool) -> Self:
        """MediaServiceUpdateV2 operation.

        Args:
            parameters (MediaServiceUpdateParameters):
                parameters parameter
            event_firing_enabled (bool):
                eventFiringEnabled parameter
        """
        qry = ServiceOperationQuery(
            self,
            "MediaServiceUpdateV2",
            None,
            {"parameters": parameters, "eventFiringEnabled": event_firing_enabled},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def recycle_with_parameters(self, parameters: ListItemDeleteParameters) -> ClientResult[UUID]:
        """RecycleWithParameters operation.

        Args:
            parameters (ListItemDeleteParameters):
                parameters parameter
        """
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(self, "RecycleWithParameters", None, {"parameters": parameters}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def render_list_item_data_as_stream(self, options: int) -> ClientResult[bytes]:
        """RenderListItemDataAsStream operation.

        Args:
            options (int):
                options parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(self, "RenderListItemDataAsStream", [options], return_type, return_raw_content=True)
        self.context.add_query(qry)
        return return_type

    def set_compliance_tag(
        self,
        compliance_tag: str,
        is_tag_policy_hold: bool,
        is_tag_policy_record: bool,
        is_event_based_tag: bool,
        is_tag_super_lock: bool,
        is_unlocked_as_default: bool,
    ) -> Self:
        """SetComplianceTag operation.

        Args:
            compliance_tag (str):
                complianceTag parameter
            is_tag_policy_hold (bool):
                isTagPolicyHold parameter
            is_tag_policy_record (bool):
                isTagPolicyRecord parameter
            is_event_based_tag (bool):
                isEventBasedTag parameter
            is_tag_super_lock (bool):
                isTagSuperLock parameter
            is_unlocked_as_default (bool):
                isUnlockedAsDefault parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetComplianceTag",
            None,
            {
                "complianceTag": compliance_tag,
                "isTagPolicyHold": is_tag_policy_hold,
                "isTagPolicyRecord": is_tag_policy_record,
                "isEventBasedTag": is_event_based_tag,
                "isTagSuperLock": is_tag_super_lock,
                "isUnlockedAsDefault": is_unlocked_as_default,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_compliance_tag_with_explicit_metas_update(
        self,
        compliance_tag: str,
        compliance_flags: int,
        compliance_tag_written_time: datetime.datetime,
        user_email_address: str,
    ) -> Self:
        """SetComplianceTagWithExplicitMetasUpdate operation.

        Args:
            compliance_tag (str):
                complianceTag parameter
            compliance_flags (int):
                complianceFlags parameter
            compliance_tag_written_time (datetime):
                complianceTagWrittenTime parameter
            user_email_address (str):
                userEmailAddress parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetComplianceTagWithExplicitMetasUpdate",
            None,
            {
                "complianceTag": compliance_tag,
                "complianceFlags": compliance_flags,
                "complianceTagWrittenTime": compliance_tag_written_time,
                "userEmailAddress": user_email_address,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_compliance_tag_with_meta_info(
        self,
        compliance_tag: str,
        block_delete: bool,
        block_edit: bool,
        compliance_tag_written_time: datetime.datetime,
        user_email_address: str,
        is_tag_super_lock: bool,
        is_record_unlocked_as_default: bool,
    ) -> Self:
        """SetComplianceTagWithMetaInfo operation.

        Args:
            compliance_tag (str):
                complianceTag parameter
            block_delete (bool):
                blockDelete parameter
            block_edit (bool):
                blockEdit parameter
            compliance_tag_written_time (datetime):
                complianceTagWrittenTime parameter
            user_email_address (str):
                userEmailAddress parameter
            is_tag_super_lock (bool):
                isTagSuperLock parameter
            is_record_unlocked_as_default (bool):
                isRecordUnlockedAsDefault parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetComplianceTagWithMetaInfo",
            None,
            {
                "complianceTag": compliance_tag,
                "blockDelete": block_delete,
                "blockEdit": block_edit,
                "complianceTagWrittenTime": compliance_tag_written_time,
                "userEmailAddress": user_email_address,
                "isTagSuperLock": is_tag_super_lock,
                "isRecordUnlockedAsDefault": is_record_unlocked_as_default,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_compliance_tag_with_no_hold(self, compliance_tag: str) -> Self:
        """SetComplianceTagWithNoHold operation.

        Args:
            compliance_tag (str):
                complianceTag parameter
        """
        qry = ServiceOperationQuery(
            self, "SetComplianceTagWithNoHold", None, {"complianceTag": compliance_tag}, None, None
        )
        self.context.add_query(qry)
        return self

    def set_compliance_tag_with_record(self, compliance_tag: str) -> Self:
        """SetComplianceTagWithRecord operation.

        Args:
            compliance_tag (str):
                complianceTag parameter
        """
        qry = ServiceOperationQuery(
            self, "SetComplianceTagWithRecord", None, {"complianceTag": compliance_tag}, None, None
        )
        self.context.add_query(qry)
        return self

    def unarchive(self) -> ClientResult[str]:
        """Unarchive operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "Unarchive", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def validate_update_fetch_list_item(
        self,
        form_values: ClientValueCollection[ListItemFormUpdateValue],
        bnew_document_update: bool,
        check_in_comment: str,
        dates_in_utc: bool,
        number_in_invariant_culture: bool,
        view: str,
        root_folder: str,
    ) -> ClientResult[ListItemUpdateResults]:
        """ValidateUpdateFetchListItem operation.

        Args:
            form_values (ClientValueCollection[ListItemFormUpdateValue]):
                formValues parameter
            bnew_document_update (bool):
                bNewDocumentUpdate parameter
            check_in_comment (str):
                checkInComment parameter
            dates_in_utc (bool):
                datesInUTC parameter
            number_in_invariant_culture (bool):
                numberInInvariantCulture parameter
            view (str):
                View parameter
            root_folder (str):
                RootFolder parameter
        """
        from office365.sharepoint.listitems.updateresults import ListItemUpdateResults

        return_type = ClientResult(self.context, ListItemUpdateResults())
        qry = ServiceOperationQuery(
            self,
            "ValidateUpdateFetchListItem",
            None,
            {
                "formValues": form_values,
                "bNewDocumentUpdate": bnew_document_update,
                "checkInComment": check_in_comment,
                "datesInUTC": dates_in_utc,
                "numberInInvariantCulture": number_in_invariant_culture,
                "View": view,
                "RootFolder": root_folder,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def validate_update_fetch_list_item_in_folder(
        self,
        form_values: ClientValueCollection[ListItemFormUpdateValue],
        bnew_document_update: bool,
        check_in_comment: str,
        dates_in_utc: bool,
        number_in_invariant_culture: bool,
        root_folder: str,
    ) -> ClientResult[ListItemUpdateResults]:
        """ValidateUpdateFetchListItemInFolder operation.

        Args:
            form_values (ClientValueCollection[ListItemFormUpdateValue]):
                formValues parameter
            bnew_document_update (bool):
                bNewDocumentUpdate parameter
            check_in_comment (str):
                checkInComment parameter
            dates_in_utc (bool):
                datesInUTC parameter
            number_in_invariant_culture (bool):
                numberInInvariantCulture parameter
            root_folder (str):
                rootFolder parameter
        """
        from office365.sharepoint.listitems.updateresults import ListItemUpdateResults

        return_type = ClientResult(self.context, ListItemUpdateResults())
        qry = ServiceOperationQuery(
            self,
            "ValidateUpdateFetchListItemInFolder",
            None,
            {
                "formValues": form_values,
                "bNewDocumentUpdate": bnew_document_update,
                "checkInComment": check_in_comment,
                "datesInUTC": dates_in_utc,
                "numberInInvariantCulture": number_in_invariant_culture,
                "rootFolder": root_folder,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_compliance_tag_v2(
        self,
        compliance_tag: str,
        is_tag_policy_hold: bool,
        is_tag_policy_record: bool,
        is_event_based_tag: bool,
        is_tag_super_lock: bool,
        is_unlocked_as_default: bool,
        do_not_enforce_tag_policy_hold_for_versions: bool,
    ) -> Self:
        """SetComplianceTagV2 operation.

        Args:
            compliance_tag (str):
                complianceTag parameter
            is_tag_policy_hold (bool):
                isTagPolicyHold parameter
            is_tag_policy_record (bool):
                isTagPolicyRecord parameter
            is_event_based_tag (bool):
                isEventBasedTag parameter
            is_tag_super_lock (bool):
                isTagSuperLock parameter
            is_unlocked_as_default (bool):
                isUnlockedAsDefault parameter
            do_not_enforce_tag_policy_hold_for_versions (bool):
                doNotEnforceTagPolicyHoldForVersions parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetComplianceTagV2",
            None,
            {
                "complianceTag": compliance_tag,
                "isTagPolicyHold": is_tag_policy_hold,
                "isTagPolicyRecord": is_tag_policy_record,
                "isEventBasedTag": is_event_based_tag,
                "isTagSuperLock": is_tag_super_lock,
                "isUnlockedAsDefault": is_unlocked_as_default,
                "doNotEnforceTagPolicyHoldForVersions": do_not_enforce_tag_policy_hold_for_versions,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self
