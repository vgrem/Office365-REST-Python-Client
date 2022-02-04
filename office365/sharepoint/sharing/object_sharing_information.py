from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.sharing.object_sharing_information_user import ObjectSharingInformationUser
from office365.sharepoint.sharing.sharing_link_info import SharingLinkInfo


class ObjectSharingInformation(BaseEntity):
    """Provides information about the sharing state of a securable object."""

    @staticmethod
    def can_current_user_share(context, doc_id):
        """Indicates whether the current user can share the document identified by docId.

        :param office365.sharepoint.client_context.ClientContext context: SharePoint client context
        :param str doc_id: Identifies the document that will be analyzed from a sharing perspective.
        """
        binding_type = ObjectSharingInformation(context)
        payload = {
            "docId": doc_id
        }
        result = ClientResult(context)
        qry = ServiceOperationQuery(binding_type, "CanCurrentUserShare", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def get_list_item_sharing_information(context, list_id, item_id, exclude_current_user=True, exclude_site_admin=True,
                                          exclude_security_groups=True, retrieve_anonymous_links=False,
                                          retrieve_user_info_details=False, check_for_access_requests=False,
                                          return_type=None):
        """
        Retrieves information about the sharing state for a given list.

        :param bool check_for_access_requests: Specifies whether the returned sharing state information will contain a URL
        to a location which describes any access requests present in the site (2), if such a URL is available.
        :param bool retrieve_user_info_details: Specifies whether the returned sharing state information will contain
        basic or detailed information about the users with permissions to the list item.
        :param bool retrieve_anonymous_links: Specifies whether the returned sharing state information will contain
        information about a URL that allows an anonymous user to access the list item.
        :param bool exclude_security_groups: Specifies whether the returned sharing state information will exclude
        information about security groups which have permissions to the list item.
        :param bool exclude_site_admin:  Specifies whether the returned sharing state information will exclude
        information about users who are site collection administrators of the site collection which contains the list.
        :param bool exclude_current_user: Specifies whether the returned sharing state information will exclude
        information about the user making the request.
        :param int item_id: The list item identifier for the list item for which the sharing state is requested.
        :param str list_id: The list identifier for the list which contains the list item for which
        the sharing state is requested.
        :param office365.sharepoint.client_context.ClientContext context: SharePoint client context
        :param BaseEntity return_type: Return type
        :return: ObjectSharingInformation
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
            "checkForAccessRequests": check_for_access_requests
        }
        if not return_type:
            return_type = binding_type
        qry = ServiceOperationQuery(binding_type, "GetListItemSharingInformation", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @property
    def sharing_links(self):
        """Indicates the collection of all available sharing links for the securable object."""
        return self.properties.get('SharingLinks', ClientValueCollection(SharingLinkInfo))

    @property
    def shared_with_users_collection(self):
        """A collection of shared with users."""
        return self.properties.get('SharedWithUsersCollection',
                                   BaseEntityCollection(self.context,
                                                        ObjectSharingInformationUser,
                                                        ResourcePath("SharedWithUsersCollection", self.resource_path)))

    def get_property(self, name, default_value=None):
        if name == "SharedWithUsersCollection":
            default_value = self.shared_with_users_collection
        elif name == "SharingLinks":
            default_value = self.sharing_links
        return super(ObjectSharingInformation, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super(ObjectSharingInformation, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "AnonymousEditLink" and self._resource_path is None:
            self._resource_path = None
        return self
