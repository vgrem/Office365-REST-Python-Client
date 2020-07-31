from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


class DownloadFileQuery(ServiceOperationQuery):

    def __init__(self, web, file_url, file_object):
        """
        A download file content query

        :type file_url: str
        :type web: office365.sharepoint.webs.web.Web
        :type file_object: typing.IO
        """

        def _construct_download_query(request):
            request.method = HttpMethod.Get

        def _process_response(response):
            """
            :type response: RequestOptions
            """
            file_object.write(response.content)

        web.context.before_execute(_construct_download_query)
        web.context.after_execute(_process_response)
        super(DownloadFileQuery, self).__init__(web, r"getFileByServerRelativeUrl('{0}')/\$value".format(file_url))
