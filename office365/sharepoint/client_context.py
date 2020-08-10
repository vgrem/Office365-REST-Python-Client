import copy

import adal

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.auth.providers.saml_token_provider import resolve_base_url
from office365.runtime.auth.token_response import TokenResponse
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.client_query import DeleteEntityQuery, UpdateEntityQuery
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.json_light_format import JsonLightFormat
from office365.runtime.odata.odata_batch_request import ODataBatchRequest
from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel
from office365.runtime.odata.odata_request import ODataRequest
from office365.sharepoint.sites.site import Site
from office365.sharepoint.webs.context_web_information import ContextWebInformation
from office365.sharepoint.webs.web import Web


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

    def __init__(self, base_url, auth_context=None):
        """
        :type base_url: str
        :type auth_context: AuthenticationContext or None
        """
        if base_url.endswith("/"):
            base_url = base_url[:len(base_url) - 1]
        super(ClientContext, self).__init__(base_url + "/_api/", auth_context)
        self.__web = None
        self.__site = None
        self._base_url = base_url
        self._contextWebInformation = None
        self._pendingRequest = ODataRequest(self, JsonLightFormat(ODataMetadataLevel.Verbose))
        self._pendingRequest.beforeExecute += self._build_modification_query

    @staticmethod
    def from_url(abs_url):
        """
        Constructs ClientContext from absolute Url

        :param str abs_url: Absolute Url to resource
        :return: ClientContext
        """
        base_url = resolve_base_url(abs_url)
        ctx = ClientContext(base_url)
        result = Web.get_web_url_from_page_url(ctx, abs_url)

        def _init_context_for_web(resp):
            ctx._base_url = result.value

        ctx.after_execute(_init_context_for_web)
        return ctx

    @staticmethod
    def connect_with_credentials(base_url, credentials):
        """
        Creates authenticated SharePoint context via user or client credentials

        :param str base_url: Url to Site or Web
        :param ClientCredential or UserCredential credentials: Credentials object """
        ctx = ClientContext(base_url).with_credentials(credentials)
        ctx.authentication_context.acquire_token_func()
        return ctx

    @staticmethod
    def connect_with_certificate(base_url, client_id, thumbprint, cert_path):
        """Creates authenticated SharePoint context via certificate credentials

        :param str cert_path: Path to A PEM encoded certificate private key.
        :param str thumbprint: Hex encoded thumbprint of the certificate.
        :param str client_id: The OAuth client id of the calling application.
        :param str base_url: Url to Site or Web
        """

        def acquire_token():
            tenant_info = get_tenant_info(base_url)
            authority_url = 'https://login.microsoftonline.com/{0}'.format(tenant_info['name'])
            auth_ctx = adal.AuthenticationContext(authority_url)
            resource = tenant_info['base_url']
            with open(cert_path, 'r') as file:
                key = file.read()
            json_token = auth_ctx.acquire_token_with_client_certificate(
                resource,
                client_id,
                key,
                thumbprint)
            return TokenResponse(**json_token)

        ctx_auth = AuthenticationContext(url=base_url)
        ctx_auth.set_token(acquire_token())
        ctx = ClientContext(base_url, ctx_auth)
        return ctx

    def with_credentials(self, credentials):
        """
        Assigns credentials

        :type credentials: UserCredential or ClientCredential
        """
        self._auth_context = AuthenticationContext(url=self._base_url)

        def _acquire_token():
            if not self.authentication_context.is_authenticated:
                if isinstance(credentials, ClientCredential):
                    return self.authentication_context.acquire_token_for_app(credentials.clientId,
                                                                             credentials.clientSecret)
                elif isinstance(credentials, UserCredential):
                    return self.authentication_context.acquire_token_for_user(credentials.userName,
                                                                              credentials.password)
                else:
                    raise ValueError("Unknown credential type")

        self._auth_context.acquire_token_func = _acquire_token
        return self

    def execute_batch(self):
        """Construct and submit a batch request"""
        batch_request = ODataBatchRequest(self, JsonLightFormat(ODataMetadataLevel.Verbose))

        def _prepare_batch_request(request):
            self.ensure_form_digest(request)

        batch_request.beforeExecute += _prepare_batch_request
        batch_request.execute_query()

    def build_request(self):
        request = super(ClientContext, self).build_request()
        self.get_pending_request().ensure_media_type(request)
        self.get_pending_request().beforeExecute.notify(request)
        return request

    def get_pending_request(self):
        """
        :return: ODataRequest
        """
        return self._pendingRequest

    def ensure_form_digest(self, request_options):
        """
        :type request_options: RequestOptions
        """
        if not self._contextWebInformation:
            self._contextWebInformation = ContextWebInformation()
            self.request_form_digest()
        request_options.set_header('X-RequestDigest', self._contextWebInformation.FormDigestValue)

    def request_form_digest(self):
        """Request Form Digest"""
        request = RequestOptions(self.service_root_url + "contextInfo")
        request.method = HttpMethod.Post
        response = self.execute_request_direct(request)
        json = response.json()
        json_format = JsonLightFormat()
        json_format.function_tag_name = "GetContextWebInformation"
        self.get_pending_request().map_json(json, self._contextWebInformation, json_format)

    def clone(self, url, clear_queries=True):
        """
        Creates a clone of ClientContext

        :param bool clear_queries:
        :param str url: Site Url
        :return ClientContext
        """
        ctx = copy.deepcopy(self)
        ctx._base_url = url
        if clear_queries:
            ctx.clear_queries()
        return ctx

    def _build_modification_query(self, request):
        """
        Constructs SharePoint specific modification OData request

        :type request: RequestOptions
        """
        query = self.current_query

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
        return self._base_url

    @property
    def authentication_context(self):
        return self._auth_context

    @property
    def service_root_url(self):
        return '/'.join(s.strip('/') for s in [self._base_url, '_api']) + '/'
