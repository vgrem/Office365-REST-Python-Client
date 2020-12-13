from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class ObjectSharingInformation(BaseEntity):

    @staticmethod
    def get_list_item_sharing_information(context, listID, itemID, excludeCurrentUser=True, excludeSiteAdmin=True,
                                          excludeSecurityGroups=True, retrieveAnonymousLinks=False,
                                          retrieveUserInfoDetails=False, checkForAccessRequests=False):
        """
        Retrieves information about the sharing state for a given list.

        :param bool checkForAccessRequests: Specifies whether the returned sharing state information will contain a URL
        to a location which describes any access requests present in the site (2), if such a URL is available.
        :param bool retrieveUserInfoDetails: Specifies whether the returned sharing state information will contain
        basic or detailed information about the users with permissions to the list item.
        :param bool retrieveAnonymousLinks: Specifies whether the returned sharing state information will contain
        information about a URL that allows an anonymous user to access the list item.
        :param bool excludeSecurityGroups: Specifies whether the returned sharing state information will exclude
        information about security groups which have permissions to the list item.
        :param bool excludeSiteAdmin:  Specifies whether the returned sharing state information will exclude
        information about users who are site collection administrators of the site collection which contains the list.
        :param bool excludeCurrentUser: Specifies whether the returned sharing state information will exclude
        information about the user making the request.
        :param int itemID: The list item identifier for the list item for which the sharing state is requested.
        :param str listID: The list identifier for the list which contains the list item for which
        the sharing state is requested.
        :param office365.sharepoint.client_context.ClientContext context:
        :return: ObjectSharingInformation
        """
        result = ObjectSharingInformation(context)
        payload = {
            "listID": listID,
            "itemID": itemID,
            "excludeCurrentUser": excludeCurrentUser,
            "excludeSiteAdmin": excludeSiteAdmin,
            "excludeSecurityGroups": excludeSecurityGroups,
            "retrieveAnonymousLinks": retrieveAnonymousLinks,
            "retrieveUserInfoDetails": retrieveUserInfoDetails,
            "checkForAccessRequests": checkForAccessRequests
        }
        qry = ServiceOperationQuery(result, "GetListItemSharingInformation", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result
