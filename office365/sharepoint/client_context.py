import adal
from office365.runtime.auth.ClientCredential import ClientCredential
from office365.runtime.auth.UserCredential import UserCredential
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.client_query import DeleteEntityQuery, UpdateEntityQuery
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.sharepoint.context_web_information import ContextWebInformation
from office365.runtime.odata.json_light_format import JsonLightFormat
from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.odata_request import ODataRequest
from office365.sharepoint.site import Site
from office365.sharepoint.web import Web


def get_tenant_info(url):
    parts = url.split('://')
    host_name = parts[1].split("/")[0]
    tenant_name = "{0}.onmicrosoft.com".format(host_name.split(".")[0])
    return {
        "base_url": "{0}://{1}".format(parts[0], host_name),
        "name": tenant_name
    }


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
        self._accessToken = None

    @classmethod
    def connect_with_credentials(cls, base_url, credentials):
        """Creates authenticated SharePoint client context"""
        ctx_auth = AuthenticationContext(url=base_url)
        if isinstance(credentials, ClientCredential):
            ctx_auth.acquire_token_for_app(client_id=credentials.clientId, client_secret=credentials.clientSecret)
        elif isinstance(credentials, UserCredential):
            ctx_auth.acquire_token_for_user(username=credentials.userName, password=credentials.password)
        else:
            raise ValueError("Unknown credential type")
        return cls(base_url, ctx_auth)

    @classmethod
    def connect_with_certificate(cls, base_url, client_id, thumbprint, cert_path):
        """Gets a token for a given resource via certificate credentials"""
        tenant_info = get_tenant_info(base_url)
        authority_url = 'https://login.microsoftonline.com/{0}'.format(tenant_info['name'])
        auth_ctx = adal.AuthenticationContext(authority_url)
        resource = tenant_info['base_url']
        with open(cert_path, 'r') as file:
            key = file.read()
        ctx = ClientContext(base_url, None)
        ctx._accessToken = auth_ctx.acquire_token_with_client_certificate(
            resource,
            client_id,
            key,
            thumbprint)
        return ctx

    def authenticate_request(self, request):
        if self._accessToken:
            request.set_header('Authorization', 'Bearer {0}'.format(self._accessToken["accessToken"]))
        else:
            super(ClientContext, self).authenticate_request(request)

    def get_pending_request(self):
        return self._pendingRequest

    def ensure_form_digest(self, request_options):
        if not self._contextWebInformation:
            self._contextWebInformation = ContextWebInformation()
            self.request_form_digest()
        request_options.set_header('X-RequestDigest', self._contextWebInformation.FormDigestValue)

    def request_form_digest(self):
        """Request Form Digest"""
        request = RequestOptions(self.service_root_url + "contextinfo")
        request.method = HttpMethod.Post
        response = self.execute_request_direct(request)
        json = response.json()
        json_format = JsonLightFormat()
        json_format.function_tag_name = "GetContextWebInformation"
        self.get_pending_request().map_json(json, self._contextWebInformation, json_format)

    def _build_specific_query(self, request):
        query = self.get_pending_request().current_query

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
    def base_url(self):
        return self.__base_url

    @property
    def service_root_url(self):
        return super(ClientContext, self).service_root_url
