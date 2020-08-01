from office365.graph.onedrive.driveItem import DriveItem
from office365.graph.resource_path_url import ResourcePathUrl
from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


class DownloadContentQuery(ServiceOperationQuery):
    def __init__(self, entity_type, format_name=None):
        """

        :type entity_type: ClientObject
        :type format_name: str or None
        """
        result = ClientResult(None)
        action_name = "content"
        if format_name is not None:
            action_name = action_name + r"?format={0}".format(format_name)
        super(DownloadContentQuery, self).__init__(entity_type, action_name, None, None, None, result)


class ReplaceMethodQuery(ServiceOperationQuery):
    pass


class UploadContentQuery(ServiceOperationQuery):
    def __init__(self, parent_entity, name, content):
        return_type = DriveItem(parent_entity.context, ResourcePathUrl(name, parent_entity.resource_path))
        super(UploadContentQuery, self).__init__(return_type, "content", None, content, None, return_type)


class SearchQuery(ServiceOperationQuery):
    def __init__(self, entity_type, query_text, return_type):
        super(SearchQuery, self).__init__(entity_type, "search", {"q": query_text}, None, None, return_type)
