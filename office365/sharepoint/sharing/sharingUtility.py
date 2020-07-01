from office365.runtime.queries.serviceOperationQuery import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sharing.userDirectoryInfo import UserDirectoryInfo


class SharingUtility(BaseEntity):

    def __init__(self, context):
        super().__init__(context, ResourcePath("SharingUtility"))

    @staticmethod
    def get_user_directory_info_by_email(context, email):
        """

        :param str email:
        :param office365.sharepoint.client_context.ClientContext context:
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
