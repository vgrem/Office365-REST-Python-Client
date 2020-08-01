from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


class UploadFileQuery(ServiceOperationQuery):

    def __init__(self, web, file_url, file_object):
        """
        A download file content query

        :type file_url: str
        :type web: office365.sharepoint.webs.web.Web
        :type file_object: typing.IO
        """
        super().__init__(web)

        def _process_response(response):
            """
            :type response: RequestOptions
            """
            file_object.write(response.content)

        def _construct_upload_request(request):
            request.data = file_object.read()
            request.method = HttpMethod.Post
            request.set_header('X-HTTP-Method', 'PUT')

        web.context.before_execute(_construct_upload_request)
        web.context.after_execute(_process_response)
        super(UploadFileQuery, self).__init__(web, r"getFileByServerRelativeUrl('{0}')/\$value".format(file_url))
