import copy

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.client_result import ClientResult
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.odata.v3.batch_request import ODataBatchV3Request
from office365.runtime.odata.request import ODataRequest
from office365.runtime.queries.delete_entity import DeleteEntityQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.queries.update_entity import UpdateEntityQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.portal.site_status import SiteStatus
from office365.sharepoint.publishing.pages.service import SitePageService
from office365.sharepoint.request_user_context import RequestUserContext
from office365.sharepoint.sites.site import Site
from office365.sharepoint.tenant.administration.hub_site_collection import HubSiteCollection
from office365.sharepoint.webs.context_web_information import ContextWebInformation
from office365.sharepoint.webs.web import Web
from office365.runtime.compat import urlparse, is_absolute_url, get_absolute_url


class ClientContext(ClientRuntimeContext):
    """SharePoint client context"""

    def __init__(self, base_url, auth_context=None):
        """
        Instantiates a SharePoint client context

        :param str base_url: Absolute Web or Site Url
        :param AuthenticationContext or None auth_context: Authentication context
        """
        super(ClientContext, self).__init__()
        if auth_context is None:
            auth_context = AuthenticationContext(url=base_url)
        self._auth_context = auth_context
        self._web = None
        self._site = None
        self._ctx_web_info = None
        self._pending_request = None

    def create_safe_url(self, orig_url, relative=True):
        """
        Creates a safe url

        :type orig_url: str
        :type relative: bool
        """
        if is_absolute_url(orig_url) and not relative:
            return orig_url

        site_path = urlparse(self.base_url).path
        root_site_url = self.base_url.replace(site_path, "")
        url = orig_url if orig_url.startswith(site_path) else "/".join([site_path, orig_url])
        return url if relative else "".join([root_site_url, url])

    @staticmethod
    def from_url(full_url):
        """
        Constructs ClientContext from absolute Url

        :param str full_url: Full Url to a resource
        :return: ClientContext
        """
        root_site_url = get_absolute_url(full_url)
        ctx = ClientContext(root_site_url)
        result = Web.get_web_url_from_page_url(ctx, full_url)

        def _init_context_for_web(resp):
            """
            :type resp: requests.Response
            """
            resp.raise_for_status()
            ctx._auth_context.url = result.value

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
        self.authentication_context.with_access_token(token_func)
        return self

    def with_user_credentials(self, username, password, allow_ntlm=False, browser_mode=False):
        """
        Assigns credentials

        :type username: str
        :type password: str
        :type allow_ntlm: bool
        :type browser_mode: bool
        """
        self.authentication_context.with_credentials(
            UserCredential(username, password),
            allow_ntlm=allow_ntlm,
            browser_mode=browser_mode)
        return self

    def with_credentials(self, credentials):
        """
        Assigns credentials

        :type credentials: UserCredential or ClientCredential
        """
        self.authentication_context.with_credentials(credentials)
        return self

    def execute_batch(self, items_per_batch=100):
        """
        Construct and submit a batch request

        :param int items_per_batch: Maximum to be selected for bulk operation
        """
        batch_request = ODataBatchV3Request(self, items_per_batch)

        def _prepare_batch_request(request):
            self.ensure_form_digest(request)

        batch_request.beforeExecute += _prepare_batch_request
        [batch_request.add_query(qry) for qry in self.pending_request()]
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
        Provides access to underlying request instance

        :return: ODataRequest
        """
        if self._pending_request is None:
            self._pending_request = ODataRequest(self, JsonLightFormat())
            self._pending_request.beforeExecute += self._build_modification_query
        return self._pending_request

    def ensure_form_digest(self, request_options):
        """
        :type request_options: RequestOptions
        """
        if not self.context_info.is_valid:
            self._ctx_web_info = self.get_context_web_information(request_options=request_options)
        request_options.set_header('X-RequestDigest', self._ctx_web_info.FormDigestValue)

    def get_context_web_information(self, request_options=None):
        """Returns an ContextWebInformation object that specifies metadata about the site"""
        request = RequestOptions("{0}/contextInfo".format(self.service_root_url()))
        request.method = HttpMethod.Post
        if request_options:
            request.proxies = request_options.proxies
            request.verify = request_options.verify
        response = self.pending_request().execute_request_direct(request)
        json = response.json()
        json_format = JsonLightFormat()
        json_format.function = "GetContextWebInformation"
        return_value = ContextWebInformation()
        self.pending_request().map_json(json, return_value, json_format)
        return return_value

    def get_context_web_information_ex(self):
        """Returns an ContextWebInformation object that specifies metadata about the site"""
        return_type = ClientResult(self, ContextWebInformation())

        def _construct_request(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            request.url = self.service_root_url() + "/contextInfo"

        qry = ServiceOperationQuery(self.web, "GetContextWebInformation", None, None, None, return_type)
        self.before_execute(_construct_request)
        self.add_query(qry)
        return return_type

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
        ctx._auth_context.url = url
        ctx._ctx_web_info = None
        if clear_queries:
            ctx.clear()
        return ctx

    def authenticate_request(self, request):
        self.authentication_context.authenticate_request(request)

    def _build_modification_query(self, request):
        """
        Constructs SharePoint specific modification OData request

        :type request: RequestOptions
        """
        query = self.pending_request().current_query

        if request.method == HttpMethod.Post:
            self.ensure_form_digest(request)
        # set custom SharePoint control headers
        if isinstance(self.pending_request().default_json_format, JsonLightFormat):
            if isinstance(query, DeleteEntityQuery):
                request.ensure_header("X-HTTP-Method", "DELETE")
                request.ensure_header("IF-MATCH", '*')
            elif isinstance(query, UpdateEntityQuery):
                request.ensure_header("X-HTTP-Method", "MERGE")
                request.ensure_header("IF-MATCH", '*')

    def create_team_site(self, alias, title, is_public=True):
        """Creates a modern SharePoint Team site

        :param str alias: Site alias which defines site url, e.g. https://contoso.sharepoint.com/teams/{alias}
        :param str title: Site title
        :param bool is_public:
        """
        result = self.group_site_manager.create_group_ex(title, alias, is_public)
        return_type = Site(self)

        def _after_site_create(resp):
            """
            :type resp: requests.Response
            """
            resp.raise_for_status()
            if result.value.SiteStatus == SiteStatus.Error:
                raise ValueError(result.value.ErrorMessage)
            elif result.value.SiteStatus == SiteStatus.Ready:
                return_type.set_property("__siteUrl", result.value.SiteUrl)

        self.after_execute(_after_site_create)
        return return_type

    def create_communication_site(self, alias, title):
        """
        Creates a modern SharePoint Communication site

        :param str alias: Site alias which defines site url, e.g. https://contoso.sharepoint.com/sites/{alias}
        :param str title: Site title
        """
        return_type = Site(self)
        result = self.site_pages.communication_site.create(alias, title)

        def _after_site_create(resp):
            """
            :type resp: requests.Response
            """
            resp.raise_for_status()
            if result.value.SiteStatus == SiteStatus.Error:
                raise ValueError("Site creation error")
            elif result.value.SiteStatus == SiteStatus.Ready:
                return_type.set_property("__siteUrl", result.value.SiteUrl)
        self.after_execute(_after_site_create)
        return return_type

    @property
    def context_info(self):
        """Returns an ContextWebInformation object that specifies metadata about the site

        :rtype: ContextWebInformation
        """
        if self._ctx_web_info is None:
            self._ctx_web_info = ContextWebInformation()
        return self._ctx_web_info

    @property
    def web(self):
        """Get Web client object"""
        if not self._web:
            self._web = Web(self)
        return self._web

    @property
    def site(self):
        """Get Site client object"""
        if not self._site:
            self._site = Site(self)
        return self._site

    @property
    def me(self):
        """Gets the user context for the present request"""
        return RequestUserContext(self, ResourcePath("Me"))

    @property
    def micro_service_manager(self):
        """Alias to MicroServiceManager"""
        from office365.sharepoint.microservice.manager import MicroServiceManager
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
    def people_manager(self):
        """Alias to PeopleManager"""
        from office365.sharepoint.userprofiles.people_manager import PeopleManager
        return PeopleManager(self)

    @property
    def profile_loader(self):
        """Alias to ProfileLoader"""
        from office365.sharepoint.userprofiles.profile_loader import ProfileLoader
        return ProfileLoader(self)

    @property
    def lists(self):
        """Alias to ListCollection. Gets information about all lists that the current user can access."""
        from office365.sharepoint.lists.collection import ListCollection
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
    def taxonomy(self):
        """Alias to TaxonomyService"""
        from office365.sharepoint.taxonomy.service import TaxonomyService
        return TaxonomyService(self)

    @property
    def search(self):
        """Alias to SearchService"""
        from office365.sharepoint.search.service import SearchService
        return SearchService(self)

    @property
    def tenant_settings(self):
        """Alias to TenantSettings"""
        from office365.sharepoint.tenant.tenant_settings import TenantSettings
        return TenantSettings.current(self)

    @property
    def tenant(self):
        from office365.sharepoint.tenant.administration.tenant import Tenant
        if self.is_tenant:
            return Tenant(self)
        else:
            admin_ctx = self.clone(self.tenant_url)
            return Tenant(admin_ctx)

    @property
    def tenant_url(self):
        root_url = get_absolute_url(self.base_url)
        if "-admin." in root_url:
            return root_url
        result = urlparse(self.base_url)
        names = str(result.netloc).split(".")
        names[0] = names[0] + "-admin"
        return result.scheme + "://" + ".".join(names)

    @property
    def is_tenant(self):
        """
        Determines whether the current site is a tenant administration site
        """
        return self.tenant_url == self.base_url

    @property
    def base_url(self):
        """Represents absolute Web or Site Url"""
        return self.authentication_context.url

    @property
    def authentication_context(self):
        return self._auth_context

    def service_root_url(self):
        return "{0}/_api".format(self.base_url)
