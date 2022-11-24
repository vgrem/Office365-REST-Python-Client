from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity import BaseEntity


class QueryPersonalizationData(BaseEntity):
    """Contains a unique identifier for the current user who is executing a search query"""

    def __init__(self, context, user_id):
        """
        :param str user_id:
        """
        static_path = ServiceOperationPath("Microsoft.SharePoint.Client.Search.Query.QueryPersonalizationData",
                                           {"guidUserIdString": user_id})
        super(QueryPersonalizationData, self).__init__(context, static_path)
