import copy
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.auth.providers.saml_token_provider import resolve_base_url
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.json_light_format import JsonLightFormat
from office365.runtime.odata.odata_batch_request import ODataBatchRequest
from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel
from office365.runtime.odata.odata_request import ODataRequest
from office365.runtime.queries.batch_query import BatchQuery
from office365.runtime.queries.delete_entity_query import DeleteEntityQuery
from office365.runtime.queries.update_entity_query import UpdateEntityQuery
from office365.sharepoint.sites.site import Site
from office365.sharepoint.webs.context_web_information import ContextWebInformation
from office365.sharepoint.webs.web import Web
from office365.runtime.compat import range_or_xrange


class ClientContext(ClientRuntimeContext):
    """SharePoint client context"""

    def __init__(self, base_url, auth_context=None):
        """
        :type base_url: str
        :type auth_context: AuthenticationContext or None
        """
        if base_url.endswith("/"):
            base_url = base_url[:len(base_url) - 1]
        if auth_context is None:
            self._auth_context = AuthenticationContext(url=base_url)
        else:
            self._auth_context = auth_context
        super(ClientContext, self).__init__()
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

    def with_client_certificate(self, tenant, client_id, thumbprint, cert_path):
        """Creates authenticated SharePoint context via certificate credentials

        :param str tenant: Tenant name
        :param str cert_path: Path to A PEM encoded certificate private key.
        :param str thumbprint: Hex encoded thumbprint of the certificate.
        :param str client_id: The OAuth client id of the calling application.
        """
        self.authentication_context.with_client_certificate(tenant, client_id, thumbprint, cert_path)
        return self

    def with_access_token(self, token_func):
        """
        :type token_func: () -> TokenResponse
        """
        self.authentication_context.register_provider(token_func)
        return self

    def with_user_credentials(self, username, password, allow_ntlm=False, browser_mode=False):
        """
        Assigns credentials

        :type username: str
        :type password: str
        :type allow_ntlm: bool
        :type browser_mode: bool
        """
        self.authentication_context.register_provider(UserCredential(username, password), allow_ntlm=allow_ntlm,
                                                      browser_mode=browser_mode)
        return self

    def with_credentials(self, credentials):
        """
        Assigns credentials

        :type credentials: UserCredential or ClientCredential
        """
        self.authentication_context.register_provider(credentials)
        return self

    def execute_batch(self, items_per_bulk=100):
        """
        Construct and submit a batch request

        :param int items_per_bulk: Maximum to be selected for bulk operation
        """
        batch_request = ODataBatchRequest(self)

        def _prepare_batch_request(request):
            self.ensure_form_digest(request)
        batch_request.beforeExecute += _prepare_batch_request

        all_queries = [qry for qry in self.pending_request()]
        for i in range_or_xrange(0, len(all_queries), items_per_bulk):
            queries = all_queries[i:i + items_per_bulk]
            batch_request.add_query(BatchQuery(self, queries))
            batch_request.execute_query()

    def build_single_request(self, query):
        """
        :type: office365.runtime.queries.client_query.ClientQuery
        """
        request = super(ClientContext, self).build_single_request(query)
        self._build_modification_query(request)
        return request

    def pending_request(self):
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
        request = RequestOptions(self.service_root_url() + "/contextInfo")
        request.method = HttpMethod.Post
        response = self.execute_request_direct(request)
        json = response.json()
        json_format = JsonLightFormat()
        json_format.function_tag_name = "GetContextWebInformation"
        self.pending_request().map_json(json, self._contextWebInformation, json_format)

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

    def authenticate_request(self, request):
        self._auth_context.authenticate_request(request)

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
                request.ensure_header("X-HTTP-Method", "DELETE")
                request.ensure_header("IF-MATCH", '*')
            elif isinstance(query, UpdateEntityQuery):
                request.ensure_header("X-HTTP-Method", "MERGE")
                request.ensure_header("IF-MATCH", '*')

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

    def service_root_url(self):
        return "{0}/_api".format(self.base_url)
