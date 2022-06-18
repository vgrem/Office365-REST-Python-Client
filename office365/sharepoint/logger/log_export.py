from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class LogExport(BaseEntity):

    def __init__(self, context):
        """This is the primary class that should be instantiated to obtain metadata about the
        logs that you can download."""
        super(LogExport, self).__init__(context, ResourcePath("Microsoft.Online.SharePoint.SPLogger.LogExport"))

    def get_files(self, partitionId, logType):
        pass

    def get_log_types(self):
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "GetLogTypes")
        self.context.add_query(qry)
        return result
