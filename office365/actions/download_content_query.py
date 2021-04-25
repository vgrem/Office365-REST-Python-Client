from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


class DownloadContentQuery(ServiceOperationQuery):
    def __init__(self, entity_type, format_name=None):
        """

        :type entity_type: office365.runtime.client_object.ClientObject
        :type format_name: str or None
        """
        result = ClientResult(entity_type.context)
        action_name = "content"
        if format_name is not None:
            action_name = action_name + r"?format={0}".format(format_name)
        super(DownloadContentQuery, self).__init__(entity_type, action_name, None, None, None, result)
