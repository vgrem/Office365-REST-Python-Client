from typing import Optional

from requests import Response
from typing_extensions import Self

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.request import ODataRequest
from office365.runtime.odata.v3.json_light_format import JsonLightFormat


class SharePointRequest(ODataRequest):
    def __init__(self, base_url):
        super().__init__(JsonLightFormat())
        self._auth_context = AuthenticationContext(url=base_url)
        self.beforeExecute += self._authenticate_request

    def execute_request(self, path):
        # type: (str) -> Response
        request_url = "{0}/_api/{1}".format(self._auth_context.url, path)
        return self.execute_request_direct(RequestOptions(request_url))

    def with_credentials(self, credentials, environment="commercial"):
        # type: (UserCredential|ClientCredential, Optional[str]) -> Self
        """
        Initializes a client to acquire a token via user or client credentials
        :type credentials: UserCredential or ClientCredential
        :param str environment: The Office 365 Cloud Environment endpoint used for authentication
            defaults to 'commercial'.
        """
        self._auth_context.with_credentials(credentials, environment=environment)
        return self

    def _authenticate_request(self, request):
        # type: (RequestOptions) -> None
        """Authenticate request"""
        self._auth_context.authenticate_request(request)
