from office365.runtime.client_query import UpdateEntityQuery, DeleteEntityQuery
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.odata.v4_json_format import V4JsonFormat
from office365.runtime.resource_path_entity import ResourcePathEntity
from office365.runtime.utilities.http_method import HttpMethod
from office365.directory.user import User


class OutlookClient(ClientRuntimeContext):
    """Office365 Outlook client context (deprecated, prefer GraphClient instead)"""

    def __init__(self, ctx_auth):
        self.__service_root_url = "https://outlook.office365.com/api/v1.0/"
        super(OutlookClient, self).__init__(self.__service_root_url, ctx_auth)
        self.json_format = V4JsonFormat("minimal")

    def execute_query(self):
        self.pending_request.before_execute_query(self._build_specific_query)
        super(OutlookClient, self).execute_query()

    @staticmethod
    def _build_specific_query(request, query):
        if isinstance(query, UpdateEntityQuery):
            request.method = HttpMethod.Patch
        elif isinstance(query, DeleteEntityQuery):
            request.method = HttpMethod.Delete

    @property
    def me(self):
        """The Me endpoint is provided as a shortcut for specifying the current user by SMTP address."""
        return User(self, ResourcePathEntity(self, None, "me"))
