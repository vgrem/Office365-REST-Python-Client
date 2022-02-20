import copy

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.auth.providers.saml_token_provider import resolve_base_url
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.client_result import ClientResult
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.odata.v3.batch_request import ODataBatchRequest
from office365.runtime.odata.odata_request import ODataRequest
from office365.runtime.queries.batch_query import BatchQuery
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.delete_entity_query import DeleteEntityQuery
from office365.runtime.queries.update_entity_query import UpdateEntityQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.publishing.site_page_service import SitePageService
from office365.sharepoint.request_user_context import RequestUserContext
from office365.sharepoint.sites.site import Site
from office365.sharepoint.tenant.administration.hub_site_collection import HubSiteCollection
from office365.sharepoint.webs.context_web_information import ContextWebInformation
from office365.sharepoint.webs.web import Web
from office365.runtime.compat import range_or_xrange


class ClientContext(ClientRuntimeContext):
    """SharePoint client context"""

    def __init__(self, base_url, auth_context=None):
        """
        :param str base_url: Absolute Web or Site Url
        :param AuthenticationContext or None auth_context: Authentication context
        """
        if base_url.endswith("/"):
            base_url = base_url[:len(base_url) - 1]
        if auth_context is None:
            self._auth_context = AuthenticationContext(authority_url=base_url)
        else:
            self._auth_context = auth_context
        super(ClientContext, self).__init__()
        self.__web = None
        self.__site = None
        self._base_url = base_url
        self.__ctx_web_info = None
        self.__pending_request = None

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
            """
            :type resp: requests.Response
            """
            resp.raise_for_status()
            ctx._base_url = result.value

        ctx.after_execute(_init_context_for_web)
        return ctx

    def with_client_certificate(self, tenant, client_id, thumbprint, cert_path, **kwargs):
        """Creates authenticated SharePoint context via certificate credentials

        :param str tenant: Tenant name
        :param str cert_path: Path to A PEM encoded certificate private key.
        :param str thumbprint: Hex encoded thumbprint of the certificate.
        :param str client_id: The OAuth client id of the calling application.
        :param list[str] scopes (optional):  Scopes requested to access a protected API (a resource)

        """
        self.authentication_context.with_client_certificate(tenant, client_id, thumbprint, cert_path, **kwargs)
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
        self.authentication_context.register_provider(
            UserCredential(username, password),
            allow_ntlm=allow_ntlm,
            browser_mode=browser_mode)
        return self

    def with_credentials(self, credentials):
        """
        Assigns credentials

        :type credentials: UserCredential or ClientCredential
        """
        self.authentication_context.register_provider(credentials)
        return self

    def execute_batch(self, items_per_batch=100):
        """
        Construct and submit a batch request

        :param int items_per_batch: Maximum to be selected for bulk operation
        """
        batch_request = ODataBatchRequest(self)

        def _prepare_batch_request(request):
            self.ensure_form_digest(request)

        batch_request.beforeExecute += _prepare_batch_request

        all_queries = [qry for qry in self.pending_request()]
        for i in range_or_xrange(0, len(all_queries), items_per_batch):
            queries = all_queries[i:i + items_per_batch]
            batch_request.add_query(BatchQuery(self, queries))
            batch_request.execute_query()
        return self

    def build_request(self, query):
        """
        :type query: office365.runtime.queries.client_query.ClientQuery
        """
        request = super(ClientContext, self).build_request(query)
        self._build_modification_query(request)
        return request

    def pending_request(self):
        """
        :return: ODataRequest
        """
        if self.__pending_request is None:
            self.__pending_request = ODataRequest(self, JsonLightFormat())
            self.__pending_request.beforeExecute += self._build_modification_query
        return self.__pending_request

    def ensure_form_digest(self, request_options):
        """
        :type request_options: RequestOptions
        """
        if self.__ctx_web_info is None or not self.__ctx_web_info.is_valid:
            self.__ctx_web_info = self.get_context_web_information(request_options=request_options)
        request_options.set_header('X-RequestDigest', self.__ctx_web_info.FormDigestValue)

    def get_context_web_information(self, request_options=None):
        """Returns an ContextWebInformation object that specifies metadata about the site"""
        request = RequestOptions("contextInfo")
        request.method = HttpMethod.Post
        if request_options:
            request.proxies = request_options.proxies
            request.verify = request_options.verify
        response = self.execute_request_direct(request)
        json = response.json()
        json_format = JsonLightFormat()
        json_format.function_tag_name = "GetContextWebInformation"
        return_value = ContextWebInformation()
        self.pending_request().map_json(json, return_value, json_format)
        return return_value

    def get_context_web_information_ex(self):
        """Returns an ContextWebInformation object that specifies metadata about the site"""
        result = ClientResult(self, ContextWebInformation())

        def _construct_request(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            request.url = self.service_root_url() + "/contextInfo"
            request.method = HttpMethod.Post
            self.pending_request().json_format.function_tag_name = "GetContextWebInformation"

        qry = ClientQuery(self, None, None, None, result)
        self.before_execute(_construct_request)
        self.add_query(qry)
        return qry

    def execute_query_with_incremental_retry(self, max_retry=5):
        """Handles throttling requests."""
        settings = {
            "timeout": 0
        }

        def _try_process_if_failed(retry, ex):
            """
            :type retry: int
            :type ex: requests.exceptions.RequestException
            """

            # check if request was throttled - http status code 429
            # or check is request failed due to server unavailable - http status code 503
            if ex.response.status_code == 429 or ex.response.status_code == 503:
                retry_after = ex.response.headers.get("Retry-After", None)
                if retry_after is not None:
                    settings["timeout"] = int(retry_after)

        self.execute_query_retry(timeout_secs=settings.get("timeout"),
                                 max_retry=max_retry,
                                 failure_callback=_try_process_if_failed)

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
            ctx.clear()
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
        if isinstance(self.pending_request().json_format, JsonLightFormat):
            if isinstance(query, DeleteEntityQuery):
                request.ensure_header("X-HTTP-Method", "DELETE")
                request.ensure_header("IF-MATCH", '*')
            elif isinstance(query, UpdateEntityQuery):
                request.ensure_header("X-HTTP-Method", "MERGE")
                request.ensure_header("IF-MATCH", '*')

    @property
    def context_info(self):
        """Returns an ContextWebInformation object that specifies metadata about the site

        :rtype: ContextWebInformation
        """
        return self.__ctx_web_info

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
    def me(self):
        """Gets the user context for the present request"""
        return RequestUserContext(self, ResourcePath("Me"))

    @property
    def micro_service_manager(self):
        """Alias to MicroServiceManager"""
        from office365.sharepoint.microservice.micro_service_manager import MicroServiceManager
        return MicroServiceManager(self, ResourcePath("microServiceManager"))

    @property
    def group_site_manager(self):
        """Alias to GroupSiteManager"""
        from office365.sharepoint.portal.group_site_manager import GroupSiteManager
        return GroupSiteManager(self, ResourcePath("groupSiteManager"))

    @property
    def group_service(self):
        """Alias to GroupService"""
        from office365.sharepoint.portal.group_service import GroupService
        return GroupService(self, ResourcePath("GroupService"))

    @property
    def lists(self):
        """Alias to ListCollection. Gets information about all lists that the current user can access."""
        from office365.sharepoint.lists.list_collection import ListCollection
        return ListCollection(self, ResourcePath("Lists"))

    @property
    def hub_sites(self):
        """Alias to HubSiteCollection. Gets information about all hub sites that the current user can access."""
        return HubSiteCollection(self, ResourcePath("hubSites"))

    @property
    def site_pages(self):
        """Alias to SitePageService. Represents a set of APIs to use for managing site pages."""
        return SitePageService(self, ResourcePath("sitePages"))

    @property
    def site_icon_manager(self):
        """Alias to Microsoft.SharePoint.Portal.SiteIconManager. """
        from office365.sharepoint.portal.site_icon_manager import SiteIconManager
        return SiteIconManager(self, ResourcePath("SiteIconManager"))

    @property
    def site_linking_manager(self):
        """Alias to Microsoft.SharePoint.Portal.SiteLinkingManager. """
        from office365.sharepoint.portal.site_linking_manager import SiteLinkingManager
        return SiteLinkingManager(self, ResourcePath("siteLinkingManager"))

    @property
    def site_manager(self):
        """Alias to SPSiteManager. Represents methods for creating and managing SharePoint sites"""
        from office365.sharepoint.portal.site_manager import SPSiteManager
        return SPSiteManager(self, ResourcePath("spSiteManager"))

    @property
    def theme_manager(self):
        """Alias to SP.Utilities.ThemeManager. Represents methods for creating and managing site theming"""
        from office365.sharepoint.portal.theme_manager import ThemeManager
        return ThemeManager(self, ResourcePath("themeManager"))

    @property
    def base_url(self):
        """Represents absolute Web or Site Url"""
        return self._base_url

    @property
    def authentication_context(self):
        return self._auth_context

    def service_root_url(self):
        return "{0}/_api".format(self.base_url)
