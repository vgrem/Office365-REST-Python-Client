from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


def create_search_query(drive_item, query_text):
    """

    :param office365.onedrive.driveItem.DriveItem drive_item:
    :param str query_text:
    """
    result = ClientResult(drive_item.context)
    qry = ServiceOperationQuery(drive_item, "search", {"q": query_text}, None, None, result)

    def _construct_query(request):
        """
        :type request: office365.runtime.http.request_options.RequestOptions
        """
        request.method = HttpMethod.Get
    drive_item.context.before_execute(_construct_query)
    return qry
