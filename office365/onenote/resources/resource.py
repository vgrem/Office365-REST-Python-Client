from office365.onenote.entity_base_model import OnenoteEntityBaseModel
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation import ServiceOperationQuery


class OnenoteResource(OnenoteEntityBaseModel):
    """An image or other file resource on a OneNote page."""

    def get_content(self):
        """Retrieve the binary data of a file or image resource object."""
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "content", None, None, None, result)

        def _construct_query(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            request.method = HttpMethod.Get
        self.context.before_execute(_construct_query)
        self.context.add_query(qry)
        return result

    @property
    def content_url(self):
        """The URL for downloading the content

        :rtype: str or None
        """
        return self.properties.get("contentUrl", None)
