from office365.runtime.client_query import UpdateEntityQuery, DeleteEntityQuery
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.odata.odata_request import ODataRequest
from office365.runtime.odata.v4_json_format import V4JsonFormat
from office365.runtime.resource_path import ResourcePath
from office365.runtime.http.http_method import HttpMethod
from office365.directory.user import User


class OutlookClient(ClientRuntimeContext):
    """Office365 Outlook client context (deprecated, prefer GraphClient instead)"""

    def __init__(self, ctx_auth):
        self.__service_root_url = "https://outlook.office365.com/api/v1.0/"
        super(OutlookClient, self).__init__(self.__service_root_url, ctx_auth)
        self._pendingRequest = ODataRequest(self, V4JsonFormat("minimal"))
        self._pendingRequest.beforeExecute += self._build_specific_query

    def get_pending_request(self):
        return self._pendingRequest

    @staticmethod
    def _build_specific_query(request, query):
        if isinstance(query, UpdateEntityQuery):
            request.method = HttpMethod.Patch
        elif isinstance(query, DeleteEntityQuery):
            request.method = HttpMethod.Delete

    @property
    def me(self):
        """The Me endpoint is provided as a shortcut for specifying the current user by SMTP address."""
        return User(self, ResourcePath("me", None))
