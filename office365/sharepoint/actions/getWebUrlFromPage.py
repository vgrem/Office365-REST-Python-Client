from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


def create_get_web_url_from_page_url_query(context, page_full_url):
    """

    :type context:type context: office365.sharepoint.client_context.ClientContext
    :type page_full_url: str
    """
    result = ClientResult(context)
    payload = {
        "pageFullUrl": page_full_url
    }
    qry = ServiceOperationQuery(context.web, "GetWebUrlFromPageUrl", None, payload, None, result)
    qry.static = True
    return qry
