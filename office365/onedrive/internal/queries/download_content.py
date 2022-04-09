from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


def create_download_content_query(file_item, format_name=None):
    """
    :type file_item: office365.onedrive.driveItem.DriveItem
    :type format_name: str or None
    """
    result = ClientResult(file_item.context)
    action_name = "content"
    if format_name is not None:
        action_name = action_name + r"?format={0}".format(format_name)
    qry = ServiceOperationQuery(file_item, action_name, None, None, None, result)

    def _construct_query(request):
        """
        :type request: office365.runtime.http.request_options.RequestOptions
        """
        request.method = HttpMethod.Get
    file_item.context.before_execute(_construct_query)
    return qry


def create_download_session_content_query(file_item, format_name=None):
    """
    :type file_item: office365.onedrive.driveItem.DriveItem
    :type format_name: str or None
    """
    action_name = "content"
    if format_name is not None:
        action_name = action_name + r"?format={0}".format(format_name)
    qry = ServiceOperationQuery(file_item, action_name)

    return qry
