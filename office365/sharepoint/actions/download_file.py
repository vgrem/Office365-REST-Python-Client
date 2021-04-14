from office365.runtime.http.http_method import HttpMethod
from office365.runtime.odata.odata_path_parser import ODataPathParser
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
            self.context.after_execute(_process_response)

        def _process_response(response):
            """
            :type response: RequestOptions
            """
            file_object.write(response.content)

        # Sharepoint Endpoint bug: https://github.com/SharePoint/sp-dev-docs/issues/2630
        file_url = ODataPathParser.encode_method_value(file_url)
                
        super(DownloadFileQuery, self).__init__(web, r"getFileByServerRelativePath(decodedurl={0})/$value".format(file_url))
    
        self.context.before_execute(_construct_download_query)
