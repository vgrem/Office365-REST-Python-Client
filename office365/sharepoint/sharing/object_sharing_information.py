from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class ObjectSharingInformation(BaseEntity):
    """Provides information about the sharing state of a securable object."""

    @staticmethod
    def get_list_item_sharing_information(context, list_id, item_id, exclude_current_user=True, exclude_site_admin=True,
                                          exclude_security_groups=True, retrieve_anonymous_links=False,
                                          retrieve_user_info_details=False, check_for_access_requests=False):
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
        :param office365.sharepoint.client_context.ClientContext context:
        :return: ObjectSharingInformation
        """
        result = ObjectSharingInformation(context)
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
        qry = ServiceOperationQuery(result, "GetListItemSharingInformation", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result
