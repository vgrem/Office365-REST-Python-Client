from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.sharing.links.info import SharingLinkInfo
from office365.sharepoint.sharing.object_sharing_information_user import (
    ObjectSharingInformationUser,
)

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext  # noqa


class ObjectSharingInformation(Entity):
    """Provides information about the sharing state of a securable object."""

    @staticmethod
    def can_current_user_share(context: ClientContext, doc_id: str) -> ClientResult[int]:
        """Indicates whether the current user can share the document identified by docId.

        Args:
            context (office365.sharepoint.client_context.ClientContext): SharePoint client context
            doc_id (str): Identifies the document that will be analyzed from a sharing perspective.
        """
        binding_type = ObjectSharingInformation(context)
        payload = {"docId": doc_id}
        return_type = ClientResult(context, int())
        qry = ServiceOperationQuery(binding_type, "CanCurrentUserShare", None, payload, None, return_type, True)
        context.add_query(qry)
        return return_type

    @staticmethod
    def can_current_user_share_remote(context: ClientContext, doc_id: str) -> ClientResult[int]:
        """Indicates whether the current user can share the document identified by docId, from a remote context.

        Args:
            context (office365.sharepoint.client_context.ClientContext): SharePoint client context
            doc_id (str): Identifies the document that will be analyzed from a sharing perspective.
        """
        binding_type = ObjectSharingInformation(context)
        payload = {"docId": doc_id}
        return_type = ClientResult(context, int())
        qry = ServiceOperationQuery(
            binding_type,
            "CanCurrentUserShareRemote",
            None,
            payload,
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_web_sharing_information(
        context: ClientContext,
        exclude_current_user=None,
        exclude_site_admin=None,
        exclude_security_groups=None,
        retrieve_anonymous_links=None,
        retrieve_user_info_details=None,
        check_for_access_requests=None,
    ):
        """Retrieves information about the sharing state for the current site. The current site is the site
        in the context of which this method is invoked.

        Args:
            context (office365.sharepoint.client_context.ClientContext): SharePoint client context
            exclude_current_user (bool): Specifies whether the returned sharing state information will exclude
            information about the user making the request.
            exclude_site_admin (bool): Specifies whether the returned sharing state information will exclude
            information about users who are site collection administrators of the site collection which contains
            the current site
            exclude_security_groups (bool): Specifies whether the returned sharing state information will exclude
            information about security groups which have permissions to the current site
            retrieve_anonymous_links (bool): This parameter is ignored by the method.
            retrieve_user_info_details (bool): Specifies whether the returned sharing state information will contain
            basic or detailed information about the users with permissions to the current site
            check_for_access_requests (bool): Specifies whether the returned sharing state information will contain a
            URL to a location which describes any access requests present in the current site,
            if such a URL is available
        """
        return_type = ObjectSharingInformation(context)
        payload = {
            "excludeCurrentUser": exclude_current_user,
            "excludeSiteAdmin": exclude_site_admin,
            "excludeSecurityGroups": exclude_security_groups,
            "retrieveAnonymousLinks": retrieve_anonymous_links,
            "retrieveUserInfoDetails": retrieve_user_info_details,
            "checkForAccessRequests": check_for_access_requests,
        }
        qry = ServiceOperationQuery(
            return_type,
            "GetWebSharingInformation",
            None,
            payload,
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    def get_shared_with_users(self):
        """Returns an array that contains the users with whom a securable object is shared."""
        return_type = EntityCollection(self.context, ObjectSharingInformationUser)
        qry = ServiceOperationQuery(self, "GetSharedWithUsers", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @staticmethod
    def get_list_item_sharing_information(
        context: ClientContext,
        list_id: str,
        item_id: int,
        exclude_current_user: Optional[bool] = True,
        exclude_site_admin: Optional[bool] = True,
        exclude_security_groups: Optional[bool] = True,
        retrieve_anonymous_links: Optional[bool] = False,
        retrieve_user_info_details: Optional[bool] = False,
        check_for_access_requests: Optional[bool] = False,
        return_type: Optional[ObjectSharingInformation] = None,
    ) -> ObjectSharingInformation:
        """Retrieves information about the sharing state for a given list.

        Args:
            check_for_access_requests: Specifies whether the returned sharing state information will contain a
            URL to a location which describes any access requests present in the site (2), if such a URL is available.
            retrieve_user_info_details: Specifies whether the returned sharing state information will contain basic
            or detailed information about the users with permissions to the list item.
            retrieve_anonymous_links: Specifies whether the returned sharing state information will contain information
            about a URL that allows an anonymous user to access the list item.
            exclude_security_groups: Specifies whether the returned sharing state information will exclude information
            about security groups which have permissions to the list item.
            exclude_site_admin: Specifies whether the returned sharing state information will exclude information
            about users who are site collection administrators of the site collection which contains the list.
            exclude_current_user: Specifies whether the returned sharing state information will exclude information
            about the user making the request.
            item_id: The list item identifier for the list item for which the sharing state is requested.
            list_id: The list identifier for the list which contains the list item for which the sharing state
            is requested.
            context: SharePoint client context
            return_type: Return type
        """
        binding_type = ObjectSharingInformation(context)
        payload = {
            "listID": list_id,
            "itemID": item_id,
            "excludeCurrentUser": exclude_current_user,
            "excludeSiteAdmin": exclude_site_admin,
            "excludeSecurityGroups": exclude_security_groups,
            "retrieveAnonymousLinks": retrieve_anonymous_links,
            "retrieveUserInfoDetails": retrieve_user_info_details,
            "checkForAccessRequests": check_for_access_requests,
        }
        if not return_type:
            return_type = binding_type
        qry = ServiceOperationQuery(
            binding_type,
            "GetListItemSharingInformation",
            None,
            payload,
            None,
            return_type,
        )
        qry.static = True
        context.add_query(qry)
        return return_type

    @property
    def anonymous_edit_link(self) -> Optional[str]:
        """
        Provides the URL that allows an anonymous user to edit the securable object.
        If such a URL is not available, this property will provide an empty string.
        """
        return self.properties.get("AnonymousEditLink", None)

    @property
    def anonymous_view_link(self) -> Optional[str]:
        """
        Provides the URL that allows an anonymous user to view the securable object.
        If such a URL is not available, this property will provide an empty string.
        """
        return self.properties.get("AnonymousViewLink", None)

    @property
    def can_be_shared(self) -> Optional[bool]:
        """
        Indicates whether the current securable object can be shared.
        """
        return self.properties.get("CanBeShared", None)

    @property
    def can_be_unshared(self) -> Optional[bool]:
        """
        Indicates whether the current securable object can be unshared.
        """
        return self.properties.get("CanBeUnshared", None)

    @property
    def can_manage_permissions(self) -> Optional[bool]:
        """
        Specifies whether the current user is allowed to change the permissions of the securable object.
        """
        return self.properties.get("CanManagePermissions", None)

    @property
    def has_pending_access_requests(self) -> Optional[bool]:
        """
        Provides information about whether there are any pending access requests for the securable object.

        This information is only provided if the current user has sufficient permissions to view any pending
        access requests. If the current user does not have such permissions, this property will return false.
        """
        return self.properties.get("HasPendingAccessRequests", None)

    @property
    def has_permission_levels(self) -> Optional[bool]:
        """
        Indicates whether the object sharing information contains permissions information in addition to the identities
        of the users who have access to the securable object.
        """
        return self.properties.get("HasPermissionLevels", None)

    @property
    def sharing_links(self) -> ClientValueCollection[SharingLinkInfo]:
        """Indicates the collection of all available sharing links for the securable object."""
        return self.properties.get("SharingLinks", ClientValueCollection(SharingLinkInfo))

    @property
    def shared_with_users_collection(
        self,
    ) -> EntityCollection[ObjectSharingInformationUser]:
        """A collection of shared with users."""
        return self.properties.get(
            "SharedWithUsersCollection",
            EntityCollection(
                self.context,
                ObjectSharingInformationUser,
                ResourcePath("SharedWithUsersCollection", self.resource_path),
            ),
        )

    def get_property(self, name, default_value=None):
        if name == "SharedWithUsersCollection":
            default_value = self.shared_with_users_collection
        elif name == "SharingLinks":
            default_value = self.sharing_links
        return super().get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super().set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "AnonymousEditLink" and self._resource_path is None:
            self._resource_path = None
        return self

    @property
    def is_folder(self) -> Optional[bool]:
        """Gets the IsFolder property"""
        return self.properties.get("IsFolder", None)

    @property
    def is_shared_with_current_user(self) -> Optional[bool]:
        """Gets the IsSharedWithCurrentUser property"""
        return self.properties.get("IsSharedWithCurrentUser", None)

    @property
    def is_shared_with_guest(self) -> Optional[bool]:
        """Gets the IsSharedWithGuest property"""
        return self.properties.get("IsSharedWithGuest", None)

    @property
    def is_shared_with_many(self) -> Optional[bool]:
        """Gets the IsSharedWithMany property"""
        return self.properties.get("IsSharedWithMany", None)

    @property
    def is_shared_with_security_group(self) -> Optional[bool]:
        """Gets the IsSharedWithSecurityGroup property"""
        return self.properties.get("IsSharedWithSecurityGroup", None)

    @property
    def pending_access_requests_link(self) -> Optional[str]:
        """Gets the PendingAccessRequestsLink property"""
        return self.properties.get("PendingAccessRequestsLink", None)

    @property
    def total_file_count(self) -> Optional[int]:
        """Gets the TotalFileCount property"""
        return self.properties.get("TotalFileCount", None)
