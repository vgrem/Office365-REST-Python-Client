from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sharing.userDirectoryInfo import UserDirectoryInfo


class SharingUtility(BaseEntity):
    """Provides sharing related utility methods."""

    def __init__(self, context):
        super(SharingUtility, self).__init__(context, ResourcePath("SharingUtility"))

    @staticmethod
    def get_user_directory_info_by_email(context, email):
        """
        Get user information by the user’s email address in directory.

        :param str email: The email address of a user.
        :param office365.sharepoint.client_context.ClientContext context: SharePoint client context
        """
        result = UserDirectoryInfo()
        payload = {
            "email": email
        }
        utility = SharingUtility(context)
        qry = ServiceOperationQuery(utility, "GetUserDirectoryInfoByEmail", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result
