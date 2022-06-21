from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation import ServiceOperationQuery


def create_download_file_query(source_file, file_object):
    """
    Constructs a query to download a file content

    :type source_file: office365.sharepoint.files.file.File
    :type file_object: typing.IO
    """
    qry = ServiceOperationQuery(source_file, "$value")

    def _process_response(response):
        """
        :type response: requests.Response
        """
        response.raise_for_status()
        file_object.write(response.content)

    def _construct_download_query(request):
        """
        :type request: office365.runtime.http.request_options.RequestOptions
        """
        request.method = HttpMethod.Get
        source_file.context.after_execute(_process_response)

    source_file.context.before_execute(_construct_download_query)
    return qry
