import copy

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.compat import urlparse, get_absolute_url
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.request import ODataRequest
from office365.runtime.odata.v3.batch_request import ODataBatchV3Request
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.delete_entity import DeleteEntityQuery
from office365.runtime.queries.update_entity import UpdateEntityQuery
from office365.sharepoint.portal.sites.status import SiteStatus
from office365.sharepoint.publishing.pages.service import SitePageService
from office365.sharepoint.request_user_context import RequestUserContext
from office365.sharepoint.sites.site import Site
from office365.sharepoint.tenant.administration.hubsites.collection import HubSiteCollection
from office365.sharepoint.webs.context_web_information import ContextWebInformation
from office365.sharepoint.webs.web import Web


class ClientContext(ClientRuntimeContext):
    """SharePoint client context (used for SharePoint v1 API)"""

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

    @staticmethod
    def from_url(full_url):
        """
        Constructs a client from absolute resource url

        :param str full_url: Absolute Url to a resource
        """
        root_site_url = get_absolute_url(full_url)
        ctx = ClientContext(root_site_url)

        def _init_context(return_type):
            ctx._auth_context.url = return_type.value
        Web.get_web_url_from_page_url(ctx, full_url).after_execute(_init_context)
        return ctx

    def with_client_certificate(self, tenant, client_id, thumbprint, cert_path=None, private_key=None, scopes=None):
        """
        Creates authenticated SharePoint context via certificate credentials

        :param str tenant: Tenant name
        :param str or None cert_path: Path to A PEM encoded certificate private key.
        :param str or None private_key: A PEM encoded certificate private key.
        :param str thumbprint: Hex encoded thumbprint of the certificate.
        :param str client_id: The OAuth client id of the calling application.
        :param list[str] or None scopes:  Scopes requested to access a protected API (a resource)

        """
        self.authentication_context.with_client_certificate(tenant, client_id, thumbprint, cert_path, private_key,
                                                            scopes)
        return self

    def with_interactive(self, tenant, client_id, scopes=None):
        """
        Initializes a client to acquire a token interactively i.e. via a local browser.

        Prerequisite: In Azure Portal, configure the Redirect URI of your
        "Mobile and Desktop application" as ``http://localhost``.

        :param str tenant: Tenant name, for example: contoso.onmicrosoft.com
        :param str client_id: The OAuth client id of the calling application.
        :param list[str] or None scopes:  Scopes requested to access a protected API (a resource)
        """
        self.authentication_context.with_interactive(tenant, client_id, scopes)
        return self

    def with_device_flow(self, tenant, client_id, scopes=None):
        """
        Initializes a client to acquire a token via device flow auth.

        :param str tenant: Tenant name, for example: contoso.onmicrosoft.com
        :param str client_id: The OAuth client id of the calling application.
        :param list[str] or None scopes:  Scopes requested to access a protected API (a resource)
        """
        self.authentication_context.with_device_flow(tenant, client_id, scopes)
        return self

    def with_access_token(self, token_func):
        """
        Initializes a client to acquire a token from a callback

        :param () -> TokenResponse token_func: A callback
        """
        self.authentication_context.with_access_token(token_func)
        return self

    def with_user_credentials(self, username, password, allow_ntlm=False, browser_mode=False):
        """
        Initializes a client to acquire a token via user credentials.


        :param str username: Typically, a UPN in the form of an email address
        :param str password: The password
        :param bool allow_ntlm: Flag indicates whether NTLM scheme is enabled. Disabled by default
        :param bool browser_mode:
        """
        self.authentication_context.with_credentials(
            UserCredential(username, password),
            allow_ntlm=allow_ntlm,
            browser_mode=browser_mode)
        return self

    def with_client_credentials(self, client_id, client_secret):
        """
        Initializes a client to acquire a token via client credentials (SharePoint App-Only)

        SharePoint App-Only is the older, but still very relevant, model of setting up app-principals.
        This model works for both SharePoint Online and SharePoint 2013/2016/2019 on-premises

        :param str client_id: The OAuth client id of the calling application
        :param str client_secret: Secret string that the application uses to prove its identity when requesting a token
        """
        self.authentication_context.with_credentials(ClientCredential(client_id, client_secret))
        return self

    def with_credentials(self, credentials):
        """
        Initializes a client to acquire a token via user or client credentials

        :type credentials: UserCredential or ClientCredential
        """
        self.authentication_context.with_credentials(credentials)
        return self

    def execute_batch(self, items_per_batch=100):
        """
        Construct and submit to a server a batch request

        :param int items_per_batch: Maximum to be selected for bulk operation
        """
        batch_request = ODataBatchV3Request(JsonLightFormat())
        batch_request.beforeExecute += self._authenticate_request
        batch_request.beforeExecute += self._ensure_form_digest
        while self.has_pending_request:
            qry = self._get_next_query(items_per_batch)
            batch_request.execute_query(qry)
        return self

    def pending_request(self):
        """
        Provides access to underlying request instance

        :return: ODataRequest
        """
        if self._pending_request is None:
            self._pending_request = ODataRequest(JsonLightFormat())
            self._pending_request.beforeExecute += self._authenticate_request
            self._pending_request.beforeExecute += self._build_modification_query
        return self._pending_request

    def _ensure_form_digest(self, request):
        """
        :type request: RequestOptions
        """
        if not self.context_info.is_valid:
            self._ctx_web_info = self._get_context_web_information()
        request.set_header('X-RequestDigest', self._ctx_web_info.FormDigestValue)

    def _get_context_web_information(self):
        """
        Returns an ContextWebInformation object that specifies metadata about the site
        """
        client = ODataRequest(JsonLightFormat())
        for e in self.pending_request().beforeExecute:
            client.beforeExecute += e
        client.beforeExecute -= self._build_modification_query
        request = RequestOptions("{0}/contextInfo".format(self.service_root_url()))
        request.method = HttpMethod.Post
        response = client.execute_request_direct(request)
        json_format = JsonLightFormat()
        json_format.function = "GetContextWebInformation"
        return_value = ContextWebInformation()
        client.map_json(response.json(), return_value, json_format)
        return return_value

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

    def _authenticate_request(self, request):
        """
        Authenticate request
        :type request: office365.runtime.http.request_options.RequestOptions
        """
        self.authentication_context.authenticate_request(request)

    def _build_modification_query(self, request):
        """
        Constructs SharePoint specific modification OData request

        :type request: RequestOptions
        """
        if request.method == HttpMethod.Post:
            self._ensure_form_digest(request)
        # set custom SharePoint control headers
        if isinstance(self.pending_request().json_format, JsonLightFormat):
            if isinstance(self.current_query, DeleteEntityQuery):
                request.ensure_header("X-HTTP-Method", "DELETE")
                request.ensure_header("IF-MATCH", '*')
            elif isinstance(self.current_query, UpdateEntityQuery):
                request.ensure_header("X-HTTP-Method", "MERGE")
                request.ensure_header("IF-MATCH", '*')

    def create_modern_site(self, title, alias, owner=None):
        """
        Creates a modern site

        :param str alias: Site alias which defines site url, e.g. https://contoso.sharepoint.com/sites/{alias}
        :param str title: Site title
        :param str or office365.sharepoint.principal.user.User owner: Site owner
        """
        return_type = Site(self)
        site_url = "{base_url}/sites/{alias}".format(base_url=get_absolute_url(self.base_url), alias=alias)
        result = self.site_manager.create(title, site_url, owner)

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

    def create_team_site(self, alias, title, is_public=True):
        """Creates a modern SharePoint Team site

        :param str alias: Site alias which defines site url, e.g. https://contoso.sharepoint.com/teams/{alias}
        :param str title: Site title
        :param bool is_public:
        """
        result = self.group_site_manager.create_group_ex(title, alias, is_public)
        return_type = Site(self)

        def _after_site_created(resp):
            """
            :type resp: requests.Response
            """
            resp.raise_for_status()
            if result.value.SiteStatus == SiteStatus.Error:
                raise ValueError(result.value.ErrorMessage)
            elif result.value.SiteStatus == SiteStatus.Ready:
                return_type.set_property("__siteUrl", result.value.SiteUrl)

        self.after_execute(_after_site_created)
        return return_type

    def create_communication_site(self, alias, title):
        """
        Creates a modern SharePoint Communication site

        :param str alias: Site alias which defines site url, e.g. https://contoso.sharepoint.com/sites/{alias}
        :param str title: Site title
        """
        return_type = Site(self)
        site_url = "{base_url}/sites/{alias}".format(base_url=get_absolute_url(self.base_url), alias=alias)

        def _after_site_created(result):
            """
            :type result: ClientResult
            """
            if result.value.SiteStatus == SiteStatus.Error:
                raise ValueError("Site creation error")
            elif result.value.SiteStatus == SiteStatus.Ready:
                return_type.set_property("__siteUrl", result.value.SiteUrl)

        self.site_pages.communication_site.create(title, site_url).after_execute(_after_site_created)
        return return_type

    @property
    def context_info(self):
        """
        Returns an ContextWebInformation object that specifies metadata about the site
        """
        if self._ctx_web_info is None:
            self._ctx_web_info = ContextWebInformation()
        return self._ctx_web_info

    @property
    def web(self):
        """
        A group of related webpages that is hosted by a server on the World Wide Web or an intranet.
        Each website has its own entry points, metadata, administration settings, and workflows.
        """
        if not self._web:
            self._web = Web(self)
        return self._web

    @property
    def site(self):
        """
        Represents a collection of sites in a Web application, including a top-level website and all its sub sites.
        """
        if not self._site:
            self._site = Site(self)
        return self._site

    @property
    def apps(self):
        """"""
        from office365.sharepoint.apps.app_collection import AppCollection
        return AppCollection(self, ResourcePath("Apps"))

    @property
    def me(self):
        """Gets the user context for the present request"""
        return RequestUserContext(self, ResourcePath("Me"))

    @property
    def ee(self):
        """Alias to EmployeeEngagement"""
        from office365.sharepoint.viva.employee_engagement import EmployeeEngagement
        return EmployeeEngagement(self)

    @property
    def employee_experience(self):
        """Alias to EmployeeExperience"""
        from office365.sharepoint.viva.employee_experience_controller import EmployeeExperienceController
        return EmployeeExperienceController(self)

    @property
    def micro_service_manager(self):
        """Alias to MicroServiceManager"""
        from office365.sharepoint.microservice.manager import MicroServiceManager
        return MicroServiceManager(self, ResourcePath("microServiceManager"))

    @property
    def directory_session(self):
        """Alias to DirectorySession"""
        from office365.sharepoint.directory.session import DirectorySession
        return DirectorySession(self)

    @property
    def models(self):
        """Alias to collection of SPMachineLearningModel"""
        from office365.sharepoint.contentcenter.machinelearning.models.collection import SPMachineLearningModelCollection
        return SPMachineLearningModelCollection(self, ResourcePath("models"))

    @property
    def group_site_manager(self):
        """Alias to GroupSiteManager"""
        from office365.sharepoint.portal.groups.site_manager import GroupSiteManager
        return GroupSiteManager(self, ResourcePath("groupSiteManager"))

    @property
    def group_service(self):
        """Alias to GroupService"""
        from office365.sharepoint.portal.groups.service import GroupService
        return GroupService(self, ResourcePath("GroupService"))

    @property
    def navigation_service(self):
        """Alias to NavigationService"""
        from office365.sharepoint.navigation.navigation_service import NavigationService
        return NavigationService(self)

    @property
    def page_diagnostics(self):
        """Alias to PageDiagnosticsController"""
        from office365.sharepoint.publishing.diagnostics.controller import PageDiagnosticsController
        return PageDiagnosticsController(self)

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
    def hub_sites_utility(self):
        """Alias to HubSitesUtility."""
        from office365.sharepoint.portal.hub_sites_utility import SPHubSitesUtility
        return SPHubSitesUtility(self, ResourcePath("HubSitesUtility"))

    @property
    def machine_learning(self):
        """Alias to SPMachineLearningHub"""
        from office365.sharepoint.contentcenter.machinelearning.hub import SPMachineLearningHub
        return SPMachineLearningHub(self, ResourcePath("machinelearning"))

    @property
    def org_news(self):
        """Alias to OrgNewsSite"""
        from office365.sharepoint.portal.organization_news import OrganizationNews
        return OrganizationNews(self, ResourcePath("OrgNews"))

    @property
    def org_news_site(self):
        """Alias to OrgNewsSite"""
        from office365.sharepoint.orgnewssite.api import OrgNewsSiteApi
        return OrgNewsSiteApi(self, ResourcePath("OrgNewsSite"))

    @property
    def search_setting(self):
        """Alias to SearchSetting"""
        from office365.sharepoint.search.setting import SearchSetting
        return SearchSetting(self)

    @property
    def site_pages(self):
        """Alias to SitePageService. Represents a set of APIs to use for managing site pages."""
        return SitePageService(self, ResourcePath("sitePages"))

    @property
    def site_icon_manager(self):
        """Alias to Microsoft.SharePoint.Portal.SiteIconManager. """
        from office365.sharepoint.portal.sites.icon_manager import SiteIconManager
        return SiteIconManager(self, ResourcePath("SiteIconManager"))

    @property
    def site_linking_manager(self):
        """Alias to Microsoft.SharePoint.Portal.SiteLinkingManager. """
        from office365.sharepoint.portal.linkedsites.manager import SiteLinkingManager
        return SiteLinkingManager(self, ResourcePath("siteLinkingManager"))

    @property
    def site_manager(self):
        """Alias to SPSiteManager. Represents methods for creating and managing SharePoint sites"""
        from office365.sharepoint.portal.sites.manager import SPSiteManager
        return SPSiteManager(self, ResourcePath("spSiteManager"))

    @property
    def social_feed_manager(self):
        """Alias to SocialFeedManager."""
        from office365.sharepoint.social.feed.manager import SocialFeedManager
        return SocialFeedManager(self)

    @property
    def home_service(self):
        """Alias to SharePointHomeServiceContextBuilder."""
        from office365.sharepoint.portal.home.service_context_builder import SharePointHomeServiceContextBuilder
        return SharePointHomeServiceContextBuilder(self, ResourcePath("sphomeservice"))

    @property
    def home_site(self):
        """Alias to SPHSite."""
        from office365.sharepoint.sites.sph_site import SPHSite
        return SPHSite(self, ResourcePath("SPHSite"))

    @property
    def publications(self):
        from office365.sharepoint.base_entity_collection import BaseEntityCollection
        from office365.sharepoint.contentcenter.machinelearning.publications.publication import SPMachineLearningPublication
        return BaseEntityCollection(self, SPMachineLearningPublication, ResourcePath("publications"))

    @property
    def social_following_manager(self):
        from office365.sharepoint.social.following.manager import SocialFollowingManager
        return SocialFollowingManager(self)

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
        from office365.sharepoint.tenant.settings import TenantSettings
        return TenantSettings.current(self)

    @property
    def viva_site_manager(self):
        from office365.sharepoint.viva.site_manager import VivaSiteManager
        return VivaSiteManager(self)

    @property
    def workflow_services_manager(self):
        """Alias to WorkflowServicesManager"""
        from office365.sharepoint.workflowservices.manager import WorkflowServicesManager
        return WorkflowServicesManager.current(self)

    @property
    def work_items(self):
        """"""
        from office365.sharepoint.contentcenter.machinelearning.workitems.collection import \
            SPMachineLearningWorkItemCollection
        return SPMachineLearningWorkItemCollection(self, ResourcePath("workitems"))

    @property
    def tenant(self):
        from office365.sharepoint.tenant.administration.tenant import Tenant
        if self.is_tenant:
            return Tenant(self)
        else:
            admin_ctx = self.clone(self.tenant_url, False)
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
