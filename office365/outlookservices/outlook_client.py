from office365.runtime.client_query import UpdateEntityQuery, DeleteEntityQuery
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.odata.odata_request import ODataRequest
from office365.runtime.odata.v4_json_format import V4JsonFormat
from office365.runtime.resource_path import ResourcePath
from office365.runtime.http.http_method import HttpMethod
from office365.graph.directory.user import User
from office365.runtime.auth.authentication_context import AuthenticationContext


class OutlookClient(ClientRuntimeContext):

    def __init__(self, auth_context):
        """
        Office365 Outlook client context
        Status: deprecated, prefer GraphClient instead

        :type auth_context: AuthenticationContext
        """
        self._resource = "https://outlook.office365.com"
        self.__service_root_url = "{resource}/api/v1.0/".format(resource=self._resource)
        super(OutlookClient, self).__init__(self.__service_root_url, auth_context)
        self._pendingRequest = ODataRequest(self, V4JsonFormat("minimal"))
        self._pendingRequest.beforeExecute += self._build_specific_query
        self._token_parameters = None

    @classmethod
    def from_tenant(cls, tenant):
        return OutlookClient(AuthenticationContext(tenant))

    def with_user_credentials(self, client_id, user_name, password):
        self._token_parameters = {
            "client_id": client_id,
            "username": user_name,
            "password": password,
            "resource": self._resource,
            "scope": ("openid", "profile", "offline_access")
        }
        return self

    def authenticate_request(self, request):
        if not self._auth_context.is_authenticated:
            self._auth_context.acquire_token_password_grant(**self._token_parameters)
        super(OutlookClient, self).authenticate_request(request)

    def get_pending_request(self):
        return self._pendingRequest

    def _build_specific_query(self, request):
        query = self.get_pending_request().current_query
        if isinstance(query, UpdateEntityQuery):
            request.method = HttpMethod.Patch
        elif isinstance(query, DeleteEntityQuery):
            request.method = HttpMethod.Delete

    @property
    def me(self):
        """The Me endpoint is provided as a shortcut for specifying the current user by SMTP address."""
        return User(self, ResourcePath("me", None))
