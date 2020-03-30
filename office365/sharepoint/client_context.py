from office365.runtime.auth.ClientCredential import ClientCredential
from office365.runtime.auth.UserCredential import UserCredential
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.client_query import DeleteEntityQuery, UpdateEntityQuery, ServiceOperationQuery
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.context_web_information import ContextWebInformation
from office365.runtime.odata.json_light_format import JsonLightFormat
from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.odata_request import ODataRequest
from office365.sharepoint.site import Site
from office365.sharepoint.web import Web


class ClientContext(ClientRuntimeContext):
    """SharePoint client context"""

    def __init__(self, base_url, auth_context):
        if base_url.endswith("/"):
            base_url = base_url[:len(base_url) - 1]
        super(ClientContext, self).__init__(base_url + "/_api/", auth_context)
        self.__web = None
        self.__site = None
        self.__base_url = base_url
        self._contextWebInformation = None
        self._pendingRequest = ODataRequest(self, JsonLightFormat(ODataMetadataLevel.Verbose))
        self._pendingRequest.beforeExecute += self._build_specific_query
        self._pendingRequest.afterExecute += self._process_specific_response

    @classmethod
    def connect_with_credentials(cls, base_url, credentials):
        """Creates authenticated SharePoint context"""
        ctx_auth = AuthenticationContext(url=base_url)
        if isinstance(credentials, ClientCredential):
            ctx_auth.acquire_token_for_app(client_id=credentials.clientId, client_secret=credentials.clientSecret)
        elif isinstance(credentials, UserCredential):
            ctx_auth.acquire_token_for_user(username=credentials.userName, password=credentials.password)
        else:
            raise ValueError("Unknown credential type")
        return cls(base_url, ctx_auth)

    def get_pending_request(self):
        return self._pendingRequest

    def ensure_form_digest(self, request_options):
        if not self._contextWebInformation:
            self.request_form_digest()
        request_options.set_header('X-RequestDigest', self._contextWebInformation.formDigestValue)

    def request_form_digest(self):
        """Request Form Digest"""
        request = RequestOptions(self.serviceRootUrl + "contextinfo")
        request.method = HttpMethod.Post
        response = self.execute_request_direct(request)
        payload = response.json()
        if self._pendingRequest.json_format.metadata == ODataMetadataLevel.Verbose:
            payload = payload['d']['GetContextWebInformation']
        self._contextWebInformation = ContextWebInformation()
        self._contextWebInformation.from_json(payload)

    def _build_specific_query(self, request, query):

        if request.method == HttpMethod.Post:
            self.ensure_form_digest(request)
        # set custom SharePoint control headers
        if isinstance(self._pendingRequest.json_format, JsonLightFormat):
            if isinstance(query, DeleteEntityQuery):
                request.set_header("X-HTTP-Method", "DELETE")
                request.set_header("IF-MATCH", '*')
            elif isinstance(query, UpdateEntityQuery):
                request.set_header("X-HTTP-Method", "MERGE")
                request.set_header("IF-MATCH", '*')
            if self._pendingRequest.json_format.metadata == ODataMetadataLevel.Verbose:
                pass

    def _process_specific_response(self, return_type):
        pass

    @property
    def web(self):
        """Get Web client object"""
        if not self.__web:
            self.__web = Web(self)
        return self.__web

    @property
    def site(self):
        """Get Site client object"""
        if not self.__site:
            self.__site = Site(self)
        return self.__site

    @property
    def baseUrl(self):
        return self.__base_url

    @property
    def serviceRootUrl(self):
        return super(ClientContext, self).serviceRootUrl
