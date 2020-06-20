from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.serviceOperationQuery import ServiceOperationQuery


class DownloadFileQuery(ServiceOperationQuery):

    def __init__(self, web, file_url, file_object):
        """

        :type file_url: str
        :type web: Web
        :type file_object: any
        """
        self.file_object = file_object
        web.context.get_pending_request().beforeExecute += self._construct_download_query
        web.context.get_pending_request().afterExecute += self._process_response
        super(DownloadFileQuery, self).__init__(web, r"getFileByServerRelativeUrl('{0}')/\$value".format(file_url))

    def _construct_download_query(self, request):
        self.binding_type.context.get_pending_request().beforeExecute -= self._construct_download_query
        request.method = HttpMethod.Get

    def _process_response(self, response):
        self.binding_type.context.get_pending_request().afterExecute -= self._process_response
        self.file_object.write(response.content)
