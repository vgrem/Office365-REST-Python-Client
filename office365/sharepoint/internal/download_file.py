from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


def create_download_file_query(source_file, file_object):
    """
    A download file content query

    :type source_file: office365.sharepoint.files.file.File
    :type file_object: typing.IO
    """
    qry = ServiceOperationQuery(source_file, "$value")

    def _process_response(response):
        """
        :type response: RequestOptions
        """
        file_object.write(response.content)

    def _construct_download_query(request):
        request.method = HttpMethod.Get
        source_file.context.after_execute(_process_response)

    source_file.context.before_execute(_construct_download_query)
    return qry
