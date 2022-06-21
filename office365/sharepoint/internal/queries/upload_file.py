from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation import ServiceOperationQuery


def create_upload_file_query(file, file_object):
    """
    Constructs upload file content query

    :type file: office365.sharepoint.files.file.File
    :type file_object: typing.IO
    """
    qry = ServiceOperationQuery(file, "$value")

    def _construct_upload_request(request):
        request.data = file_object.read()
        request.method = HttpMethod.Post
        request.set_header('X-HTTP-Method', 'PUT')
    file.context.before_execute(_construct_upload_request)
    return qry
