from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union
from urllib.parse import urlparse

import requests
from typing_extensions import Self

from office365.azure_env import AzureEnvironment
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.auth.certificate import CertificateData
from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.auth.token_response import TokenResponse
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.client_object import ClientObject
from office365.runtime.client_result import ClientResult
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.http.url import get_absolute_url
from office365.runtime.odata.v3.batch_request import DEFAULT_MAX_BATCH_BYTES, ODataBatchV3Request
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.deferred import DeferredOperationQuery
from office365.runtime.transport.base import NoTimeoutType
from office365.runtime.transport.requests_transport import DEFAULT_POOL_CONNECTIONS, DEFAULT_POOL_MAXSIZE
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.exceptions import SecurityValidationException
from office365.sharepoint.portal.groups.creation_params import GroupCreationParams
from office365.sharepoint.portal.groups.site_info import GroupSiteInfo
from office365.sharepoint.portal.sites.creation_response import SPSiteCreationResponse
from office365.sharepoint.portal.sites.status import SiteStatus
from office365.sharepoint.principal.users.user import User
from office365.sharepoint.publishing.pages.service import SitePageService
from office365.sharepoint.publishing.sites.communication.creation_response import (
    CommunicationSiteCreationResponse,
)
from office365.sharepoint.request import SharePointRequest
from office365.sharepoint.request_user_context import RequestUserContext
from office365.sharepoint.sites.site import Site
from office365.sharepoint.tenant.administration.hubsites.collection import (
    HubSiteCollection,
)
from office365.sharepoint.thresholds import Limits, limit
from office365.sharepoint.ui.applicationpages.peoplepicker.web_service_interface import (
    ClientPeoplePickerWebServiceInterface,
    PeoplePickerWebServiceInterface,
)
from office365.sharepoint.webs.context_web_information import ContextWebInformation
from office365.sharepoint.webs.web import Web

if TYPE_CHECKING:
    from office365.runtime.queries.batch import BatchQuery
    from office365.runtime.queries.client_query import ClientQuery
    from office365.sharepoint.brandcenter.brand_center import BrandCenter
    from office365.sharepoint.portal.theme_manager import ThemeManager
    from office365.sharepoint.search.service import SearchService
    from office365.sharepoint.server_settings import ServerSettings
    from office365.sharepoint.tenant.administration.tenant import Tenant
    from office365.sharepoint.tenant.settings import TenantSettings
    from office365.sharepoint.viva.site_manager import VivaSiteManager


class ClientContext(ClientRuntimeContext):
    """SharePoint client context (SharePoint v1 API)"""

    def __init__(
        self,
        base_url: str,
        environment: Optional[AzureEnvironment] = None,
        allow_ntlm: bool = False,
        browser_mode: bool = False,
        authority: Optional[str] = None,
    ) -> None:
        """Instantiates a SharePoint client context

        Args:
            base_url (str): Absolute Web or Site Url
            authority (str or None): Override the MSAL authority URL (e.g. https://<tenant>.ciamlogin.com)
        """
        super().__init__()
        self._base_url: str = base_url.rstrip("/")
        self._environment: AzureEnvironment = environment or AzureEnvironment.Global
        self._web: Web | None = None
        self._site: Site | None = None
        self._allow_ntlm: bool = allow_ntlm
        self._browser_mode: bool = browser_mode
        self._authority: Optional[str] = authority

    @staticmethod
    def from_url(full_url: str) -> ClientContext:
        """Constructs a client from absolute resource url

        Args:
            full_url (str): Absolute Url to a resource
        """
        root_site_url = get_absolute_url(full_url)
        ctx = ClientContext(root_site_url)

        def _init_context(return_type):
            ctx.pending_request().set_base_url(return_type.value)

        Web.get_web_url_from_page_url(ctx, full_url).after_execute(_init_context)
        return ctx

    def with_client_secret(
        self,
        tenant: str,
        client_id: str,
        client_secret: str,
        scopes: Optional[List[str]] = None,
    ) -> Self:
        """Initializes a client to acquire a token via client secret (MSAL app-only).

        Args:
            tenant: Tenant name, e.g. "contoso.onmicrosoft.com"
            client_id: Application client ID
            client_secret: Client secret value
            scopes: Scopes requested to access a protected API (optional)
        """
        self.authentication_context.with_client_secret(tenant, client_id, client_secret, scopes)
        return self

    def with_client_certificate(
        self,
        tenant: str,
        client_id: str,
        thumbprint: Optional[str] = None,
        cert_path: Optional[str] = None,
        private_key: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        passphrase: Optional[str] = None,
        *,
        public_certificate: Optional[CertificateData] = None,
        use_sni: bool = False,
    ) -> Self:
        """Creates authenticated SharePoint context via certificate credentials

        Args:
            tenant (str): Tenant name
            cert_path (str or None): Path to A PEM encoded certificate private key.
            private_key (str or None): A PEM encoded certificate private key.
            thumbprint (str): Hex encoded thumbprint of the certificate (optional
                when ``public_certificate`` is given).
            client_id (str): The OAuth client id of the calling application.
            scopes (list[str] or None): Scopes requested to access a protected API (a resource)
            passphrase (str): Passphrase if the private_key is encrypted
            public_certificate: Certificate (DER/PEM bytes, inline PEM text, or a
                path) used to derive the thumbprint or, with ``use_sni``, for
                subject name/issuer authentication
            use_sni (bool): Use subject name/issuer authentication (requires the
                optional ``cryptography`` package)
        """
        self.authentication_context.with_client_certificate(
            tenant,
            client_id,
            thumbprint,
            cert_path,
            private_key,
            scopes,
            passphrase,
            public_certificate=public_certificate,
            use_sni=use_sni,
        )
        return self

    def with_interactive(self, tenant: str, client_id: str, scopes: Optional[List[str]] = None) -> Self:
        """Initializes a client to acquire a token interactively i.e. via a local browser.

        Prerequisite: In Azure Portal, configure the Redirect URI of your
        "Mobile and Desktop application" as ``http://localhost``.

        Args:
            tenant (str): Tenant name, for example: contoso.onmicrosoft.com
            client_id (str): The OAuth client id of the calling application.
            scopes (list[str] or None): Scopes requested to access a protected API (a resource)
        """
        self.authentication_context.with_interactive(tenant, client_id, scopes)
        return self

    def with_device_flow(self, tenant: str, client_id: str, scopes: Optional[List[str]] = None) -> Self:
        """Initializes a client to acquire a token via device flow auth.

        Args:
            tenant (str): Tenant name, for example: contoso.onmicrosoft.com
            client_id (str): The OAuth client id of the calling application.
            scopes (list[str] or None): Scopes requested to access a protected API (a resource)
        """
        self.authentication_context.with_device_flow(tenant, client_id, scopes)
        return self

    def with_access_token(self, token_func: Callable[[], TokenResponse | Dict[str, Any] | None]) -> Self:
        """Initializes a client to acquire a token from a callback

        The callback is invoked lazily and its result cached; acquisition is
        thread-safe (single-flight), so it is safe to use under concurrent batches.

        Args:
            token_func: A token callback returning a token response
        """
        self.authentication_context.with_access_token(token_func)
        return self

    def with_transport(
        self,
        proxies: dict[str, str] | None = None,
        verify: bool | str | None = None,
        timeout: float | tuple[float, float | None] | NoTimeoutType | None = None,
        session: requests.Session | None = None,
        *,
        pool_connections: int = DEFAULT_POOL_CONNECTIONS,
        pool_maxsize: int = DEFAULT_POOL_MAXSIZE,
        pool_block: bool = False,
    ) -> Self:
        """Configure the HTTP transport (proxy, SSL, timeout, custom session).

        Note:
            MSAL authentication requests to ``login.microsoftonline.com`` use
            their own HTTP client.  Use the ``HTTPS_PROXY`` environment variable
            to route MSAL traffic through a proxy.

        Args:
            proxies: Proxy URLs (e.g. ``{"https": "http://proxy:8080"}``)
            verify: SSL verification — ``True``, ``False``, or a CA bundle path.
                ``None`` (default) defers to the session/environment default.
            timeout: Request timeout — a number or a ``(connect, read)`` tuple.
                When ``None`` the bundled default (10 s connect, unbounded read)
                applies; pass
                :data:`~office365.runtime.transport.base.NO_TIMEOUT` to disable.
            session: Custom ``requests.Session`` with pre-configured adapters
                   (e.g. for NTLM/SSPI auth, custom TLS, connection pooling)
            pool_connections: Host connection pools kept per session (ignored
                when ``session`` is supplied)
            pool_maxsize: Maximum connections per host pool (ignored when
                ``session`` is supplied)
            pool_block: Block when a pool is full instead of discarding the
                connection (ignored when ``session`` is supplied)

        Returns:
            Self: Supports method chaining
        """
        self.pending_request().with_transport(
            proxies=proxies,
            verify=verify,
            timeout=timeout,
            session=session,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            pool_block=pool_block,
        )
        return self

    def with_user_credentials(self, username: str, password: str) -> Self:
        """Initializes a client to acquire a token via user credentials (NTLM).

        Only for **on-premises** SharePoint — construct the context with
        ``ClientContext(url, allow_ntlm=True)``. For SharePoint Online this raises:
        the legacy SAML/ACS flow is retired, use :meth:`with_username_and_password`.

        Args:
            username (str): A UPN, or ``DOMAIN\\user`` for NTLM
            password (str): The password
        """
        self.authentication_context.with_credentials(UserCredential(username, password))
        return self

    def with_username_and_password(self, tenant: str, client_id: str, username: str, password: str) -> Self:
        """Initializes a client to acquire a token via Username and password authentication flow.

        Args:
            tenant (str): Tenant name or identifier, for example: contoso.onmicrosoft.com
            client_id (str): The OAuth client id of the calling application.
            username (str): Typically, a UPN in the form of an email address
            password (str): The password
        """
        resource = get_absolute_url(self.base_url)
        scopes = [f"{resource}/.default"]
        self.authentication_context.with_username_and_password(tenant, client_id, username, password, scopes)
        return self

    def with_client_credentials(self, client_id: str, client_secret: str) -> Self:
        """Initializes a client to acquire a token via client credentials (SharePoint App-Only)

        SharePoint App-Only is the older, but still very relevant, model of setting up app-principals.
        This model works for both SharePoint Online and SharePoint 2013/2016/2019 on-premises

        Args:
            client_id (str): The OAuth client id of the calling application
            client_secret (str): Secret string that the application uses to prove its identity when requesting a token
        """
        self.authentication_context.with_credentials(ClientCredential(client_id, client_secret))
        return self

    def with_cookies(self, cookie_source, ttl_seconds=None):
        """Initializes authentication using browser-session cookies.

        Args:
            cookie_source: Callable returning Dict[str, str] or an AuthCookies instance.
            ttl_seconds: Optional max age for cached cookies before reloading from source.
        """
        self.authentication_context.with_cookies(cookie_source, ttl_seconds)
        return self

    def with_credentials(self, credentials: Union[UserCredential, ClientCredential]) -> Self:
        """
        Initializes a client to acquire a token via user or client credentials
        """
        self.authentication_context.with_credentials(credentials)
        return self

    @limit(Limits.BATCH_ITEMS, arg="items_per_batch")
    def execute_batch(
        self,
        items_per_batch: int = Limits.BATCH_ITEMS.value,
        success_callback: Optional[Callable[[List[ClientObject | ClientResult]], None]] = None,
        concurrency: int = 1,
        max_batch_bytes: Optional[int] = None,
    ) -> Self:
        """Construct and submit to a server a batch request

        With ``concurrency`` > 1 the batches run on a thread pool; each batch
        is an independent HTTP request. Batches are capped by item count
        (``items_per_batch``) and by estimated payload size (``max_batch_bytes``).
        Throttled sub-requests (HTTP 429/503) are retried individually, honoring
        ``Retry-After`` — only the failed sub-requests are re-sent, so successful
        writes aren't re-applied. ``success_callback`` runs on the caller thread
        as each batch completes (completion order when concurrent).

        Args:
            items_per_batch (int): Maximum to be selected for bulk operation
            success_callback ((List[ClientObject|ClientResult])-> None): A success callback
            concurrency (int): Maximum number of concurrent batch requests (default 1)
            max_batch_bytes (int or None): Maximum estimated batch payload size (default ~1 MB)
        """
        max_bytes = DEFAULT_MAX_BATCH_BYTES if max_batch_bytes is None else max_batch_bytes
        request = self.pending_request()
        request.warm_up()  # fetch the form digest once before dispatching any batch
        if concurrency <= 1:
            batch_request = ODataBatchV3Request(
                self._base_url, JsonLightFormat(), transport=self.pending_request().transport
            )
            batch_request.beforeExecute += request._authenticate_request
            batch_request.beforeExecute += request.ensure_form_digest
            while self.has_pending_request:
                queries, barrier = self._take_batch_round()
                self._run_batch_round(batch_request, queries, items_per_batch, max_bytes, concurrency, success_callback)
                if barrier is not None:
                    self._resolve_deferred(barrier)
            return self

        while self.has_pending_request:
            queries, barrier = self._take_batch_round()
            self._run_batch_round(None, queries, items_per_batch, max_bytes, concurrency, success_callback)
            if barrier is not None:
                self._resolve_deferred(barrier)
        return self

    @limit(Limits.BATCH_ITEMS, arg="items_per_batch")
    async def execute_batch_async(
        self,
        items_per_batch: int = Limits.BATCH_ITEMS.value,
        success_callback: Optional[Callable[[List[ClientObject | ClientResult]], None]] = None,
        concurrency: int = 1,
        max_batch_bytes: Optional[int] = None,
    ) -> Self:
        """Async counterpart of :meth:`execute_batch`.

        Pending queries are split exactly like the synchronous method, but each
        batch's HTTP round-trip runs off the event loop, so the loop is never
        blocked and independent batches overlap when ``concurrency`` > 1. Retry,
        form-digest handling and per-sub-request throttling behave as in the
        synchronous path.

        Args:
            items_per_batch (int): Maximum to be selected for bulk operation
            success_callback ((List[ClientObject|ClientResult])-> None): A success callback
            concurrency (int): Maximum number of concurrent batch requests (default 1)
            max_batch_bytes (int or None): Maximum estimated batch payload size (default ~1 MB)
        """
        max_bytes = DEFAULT_MAX_BATCH_BYTES if max_batch_bytes is None else max_batch_bytes
        request = self.pending_request()
        # fetch the form digest once before dispatching any batch (off the loop)
        await request.warm_up_async()
        while self.has_pending_request:
            queries, barrier = self._take_batch_round()
            await self._run_batch_round_async(
                request, queries, items_per_batch, max_bytes, concurrency, success_callback
            )
            if barrier is not None:
                with self.current_query_scope(barrier):
                    await barrier.execute_query_async(request)
        return self

    def _take_batch_round(self) -> "tuple[list[ClientQuery], Optional[DeferredOperationQuery]]":
        """Pop the next run of batchable queries, stopping at a deferred barrier.

        Consecutive real queries are collected for one HTTP round. The first
        :class:`~office365.runtime.queries.deferred.DeferredOperationQuery`
        encountered terminates the run and is returned to the caller, so the
        collected requests are dispatched *before* the barrier resolves. This
        mirrors ``execute_query`` ordering, where a barrier's handlers only run
        once the preceding request has completed, and lets the caller loop until
        the queue -- including follow-up queries enqueued by response handlers --
        is drained.

        Returns:
            Tuple of (batchable queries, terminating barrier or ``None``).
        """
        queries: list[ClientQuery] = []
        while self.has_pending_request:
            qry = self._queries.popleft()
            if isinstance(qry, DeferredOperationQuery):
                return queries, qry
            queries.append(qry)
        return queries, None

    def _partition_batches(
        self, queries: "list[ClientQuery]", items_per_batch: int, max_batch_bytes: int
    ) -> "list[BatchQuery]":
        """Split batchable queries into independent batch units."""
        from office365.runtime.odata.batch_util import partition_by_limits
        from office365.runtime.queries.batch import BatchQuery

        return [BatchQuery(self, chunk) for chunk in partition_by_limits(queries, items_per_batch, max_batch_bytes)]

    def _resolve_deferred(self, barrier: DeferredOperationQuery) -> None:
        """Resolve a deferred barrier in place, firing its handlers.

        Exposes the placeholder as the current query so its ``after_execute``
        handlers resolve to it, then runs it as a no-op (or the deferred op).
        Any queries those handlers enqueue are picked up by the next round.
        """
        with self.current_query_scope(barrier):
            barrier.execute_query(self.pending_request())

    def _run_batch_round(
        self,
        batch_request: Optional[ODataBatchV3Request],
        queries: "list[ClientQuery]",
        items_per_batch: int,
        max_batch_bytes: int,
        concurrency: int,
        success_callback: Optional[Callable[[List[ClientObject | ClientResult]], None]],
    ) -> None:
        """Dispatch one round's queries in submission order.

        Consecutive batchable queries are grouped into ``/_api/$batch`` requests;
        a query flagged ``batchable = False`` (an endpoint the batch service
        rejects, such as ``listdata.svc``) is executed on its own. Preceding
        batchable queries are flushed first, so mixed rounds stay ordered.

        Args:
            batch_request: Shared v3 batch request for sequential execution, or
                ``None`` when ``concurrency`` > 1 (each batch builds its own).
            queries: Queries collected for this round.
            items_per_batch: Maximum queries per batch.
            max_batch_bytes: Maximum estimated batch payload size.
            concurrency: Maximum number of concurrent batch requests.
            success_callback: Called with each completed unit's return types.
        """
        pending: list[ClientQuery] = []
        for qry in queries:
            if getattr(qry, "batchable", True):
                pending.append(qry)
                continue
            self._flush_batch_group(
                batch_request, pending, items_per_batch, max_batch_bytes, concurrency, success_callback
            )
            pending = []
            self._execute_single(qry, success_callback)
        self._flush_batch_group(batch_request, pending, items_per_batch, max_batch_bytes, concurrency, success_callback)

    def _flush_batch_group(
        self,
        batch_request: Optional[ODataBatchV3Request],
        queries: "list[ClientQuery]",
        items_per_batch: int,
        max_batch_bytes: int,
        concurrency: int,
        success_callback: Optional[Callable[[List[ClientObject | ClientResult]], None]],
    ) -> None:
        """Partition and dispatch a run of consecutive batchable queries."""
        if not queries:
            return
        batches = self._partition_batches(queries, items_per_batch, max_batch_bytes)
        if concurrency <= 1:
            assert batch_request is not None
            for batch_qry in batches:
                self._run_batch(batch_request, batch_qry)
                if callable(success_callback):
                    success_callback(batch_qry.return_types)
        else:
            self._execute_batches_in_parallel(batches, concurrency, success_callback)

    def _execute_single(
        self,
        query: "ClientQuery",
        success_callback: Optional[Callable[[List[ClientObject | ClientResult]], None]] = None,
    ) -> None:
        """Execute a non-batchable query through the pending request, in order."""
        with self.current_query_scope(query):
            self.pending_request().execute_query(query)
        if callable(success_callback) and query.return_type is not None:
            success_callback([query.return_type])

    async def _run_batch_round_async(
        self,
        request: SharePointRequest,
        queries: "list[ClientQuery]",
        items_per_batch: int,
        max_batch_bytes: int,
        concurrency: int,
        success_callback: Optional[Callable[[List[ClientObject | ClientResult]], None]],
    ) -> None:
        """Async twin of :meth:`_run_batch_round`."""
        pending: list[ClientQuery] = []
        for qry in queries:
            if getattr(qry, "batchable", True):
                pending.append(qry)
                continue
            await self._flush_batch_group_async(pending, items_per_batch, max_batch_bytes, concurrency, success_callback)
            pending = []
            with self.current_query_scope(qry):
                await request.execute_query_async(qry)
            if callable(success_callback) and qry.return_type is not None:
                success_callback([qry.return_type])
        await self._flush_batch_group_async(pending, items_per_batch, max_batch_bytes, concurrency, success_callback)

    async def _flush_batch_group_async(
        self,
        queries: "list[ClientQuery]",
        items_per_batch: int,
        max_batch_bytes: int,
        concurrency: int,
        success_callback: Optional[Callable[[List[ClientObject | ClientResult]], None]],
    ) -> None:
        """Async twin of :meth:`_flush_batch_group`."""
        if not queries:
            return
        batches = self._partition_batches(queries, items_per_batch, max_batch_bytes)
        await self._run_batches_async(batches, concurrency, success_callback)

    def _run_batch(self, batch_request: ODataBatchV3Request, batch_qry: "BatchQuery") -> None:
        """Execute one batch, refreshing an expired form digest once and retrying."""
        try:
            batch_request.execute_query_with_retry(batch_qry)
        except SecurityValidationException:
            self.pending_request().invalidate_digest()
            self.pending_request().warm_up()
            batch_request.execute_query_with_retry(batch_qry)

    def _execute_batch(self, batch_qry: "BatchQuery") -> list[Any]:
        """Execute a single batch unit on a worker thread (with per-request retry)."""
        batch_request = ODataBatchV3Request(
            self._base_url, JsonLightFormat(), transport=self.pending_request().transport
        )
        batch_request.beforeExecute += self.pending_request()._authenticate_request
        batch_request.beforeExecute += self.pending_request().ensure_form_digest
        self._run_batch(batch_request, batch_qry)
        return batch_qry.return_types

    async def _run_batch_async(self, batch_request: ODataBatchV3Request, batch_qry: "BatchQuery") -> None:
        """Execute one batch, refreshing an expired form digest once and retrying."""
        try:
            await batch_request.execute_query_with_retry_async(batch_qry)
        except SecurityValidationException:
            self.pending_request().invalidate_digest()
            await self.pending_request().warm_up_async()
            await batch_request.execute_query_with_retry_async(batch_qry)

    async def _execute_batch_async(self, batch_qry: "BatchQuery") -> list[Any]:
        """Execute a single batch unit through the async transport.

        Unlike the base implementation (which offloads the whole synchronous
        batch to a worker thread), this awaits the v3 batch's own async retry
        loop, so a native async transport configured on the context is used.
        """
        request = self.pending_request()
        batch_request = ODataBatchV3Request(self._base_url, JsonLightFormat(), transport=request.transport)
        batch_request.beforeExecute += request._authenticate_request
        batch_request.beforeExecute += request.ensure_form_digest
        batch_request._async_authenticate = request._async_authenticate
        if request.has_async_transport:
            batch_request.with_async_transport(request.async_transport)
        await self._run_batch_async(batch_request, batch_qry)
        return batch_qry.return_types

    def pending_request(self) -> SharePointRequest:
        """Provides access to underlying request instance"""
        if self._pending_request is None:
            self._pending_request = SharePointRequest(
                base_url=self._base_url,
                environment=self._environment,
                allow_ntlm=self._allow_ntlm,
                browser_mode=self._browser_mode,
                authority=self._authority,
            )
        return self._pending_request  # type: ignore[return-value]

    def execute_query_with_incremental_retry(self, max_retry=5, max_delay=None, jitter: bool = True):
        """Handles throttling requests.

        Args:
            max_retry: Maximum number of retry attempts
            max_delay: Optional cap on the exponential delay (seconds)
            jitter: Whether to randomize the delay (default True)
        """
        from office365.runtime.retry import retry_after_delay

        self.execute_query_retry(
            max_retry=max_retry,
            max_delay=max_delay,
            jitter=jitter,
            failure_callback=lambda _retry, ex: retry_after_delay(ex),
        )

    async def execute_query_with_incremental_retry_async(
        self, max_retry: int = 5, max_delay=None, jitter: bool = True
    ) -> None:
        """Async counterpart of :meth:`execute_query_with_incremental_retry`.

        Retries throttled requests (HTTP 429/503) after the server's
        ``Retry-After`` delay, awaiting ``asyncio.sleep`` so the event loop stays
        free while it waits.

        Args:
            max_retry: Maximum number of retry attempts
            max_delay: Optional cap on the exponential delay (seconds)
            jitter: Whether to randomize the delay (default True)
        """
        from office365.runtime.retry import retry_after_delay

        await self.execute_query_async_retry(
            max_retry=max_retry,
            max_delay=max_delay,
            jitter=jitter,
            failure_callback=lambda _retry, ex: retry_after_delay(ex),
        )

    def clone(self, url: str, clear_queries: bool = True) -> ClientContext:
        """Creates a clone of ClientContext for a new site URL.

        The clone reuses the source's authentication context and HTTP transport
        (shared by reference, thread-safe under concurrent batches), while
        starting with a fresh pending-query queue and per-site form digest.

        Args:
            url (str): Site Url
            clear_queries (bool): Whether to drop pending queries (default True)
        """
        ctx = ClientContext(
            url,
            environment=self._environment,
            allow_ntlm=self._allow_ntlm,
            browser_mode=self._browser_mode,
            authority=self._authority,
        )
        ctx.pending_request().reuse(self.pending_request())
        if not clear_queries:
            ctx._queries = copy.copy(self._queries)
        return ctx

    def create_modern_site(self, title: str, alias: str, owner: Optional[Union[str, User]] = None) -> Site:
        """Creates a modern (Communication) site
        https://learn.microsoft.com/en-us/sharepoint/dev/apis/site-creation-rest#create-a-modern-site

        Args:
            alias (str): Site alias which defines site url, e.g. https://contoso.sharepoint.com/sites/{alias}
            title (str): Site title
            owner (str or office365.sharepoint.principal.user.User): Site owner
        """
        return_type = Site(self)
        site_url = f"{get_absolute_url(self.base_url)}/sites/{alias}"

        def _after_site_create(result: ClientResult[SPSiteCreationResponse]) -> None:
            if result.value.SiteStatus == SiteStatus.Error:
                raise ValueError(result.value)
            elif result.value.SiteStatus == SiteStatus.Ready:
                return_type.set_property("__siteUrl", result.value.SiteUrl)

        (self.site_manager.create(title, site_url, owner).after_execute(_after_site_create))
        return return_type

    def create_team_site(
        self, alias: str, title: str, is_public: bool = True, owners: Optional[List[str]] = None
    ) -> Site:
        """Creates a modern SharePoint Team site

        Args:
            alias (str): Site alias which defines site url, e.g. https://contoso.sharepoint.com/teams/{alias}
            title (str): Site title
            is_public (bool):
        """
        return_type = Site(self)

        def _after_site_created(result: ClientResult[GroupSiteInfo]) -> None:
            if result.value.SiteStatus == SiteStatus.Error:
                raise ValueError(result.value.ErrorMessage)
            elif result.value.SiteStatus == SiteStatus.Ready:
                return_type.set_property("__siteUrl", result.value.SiteUrl)

        opt_params = GroupCreationParams(Owners=StringCollection(owners or []))
        self.group_site_manager.create_group_ex(title, alias, is_public, opt_params).after_execute(_after_site_created)
        return return_type

    def create_communication_site(self, alias: str, title: str) -> Site:
        """Creates a modern SharePoint Communication site

        Args:
            alias (str): Site alias which defines site url, e.g. https://contoso.sharepoint.com/sites/{alias}
            title (str): Site title
        """
        return_type = Site(self)
        site_url = f"{get_absolute_url(self.base_url)}/sites/{alias}"

        def _after_site_created(
            result: ClientResult[CommunicationSiteCreationResponse],
        ) -> None:
            if result.value.SiteStatus == SiteStatus.Error:
                raise ValueError("Site creation error")
            elif result.value.SiteStatus == SiteStatus.Ready:
                return_type.set_property("__siteUrl", result.value.SiteUrl)

        self.site_pages.communication_site.create(title, site_url).after_execute(_after_site_created)
        return return_type

    def search_user(self, query: str) -> ClientResult[dict[str, str]]:
        """Search/resolve user by email or display name"""

        return_type = ClientResult[dict](self)

        def _search_user(result: ClientResult[str]) -> None:
            import json

            entries = json.loads(result.value)
            if not entries or not entries[0].get("IsResolved", False):
                raise Exception(f"User '{query}' not found or could not be resolved")

            return_type.set_property("__value", entries)

        ClientPeoplePickerWebServiceInterface.client_people_picker_search_user(self, query).after_execute(_search_user)
        return return_type

    @property
    def context_info(self) -> ContextWebInformation:
        """Returns a ContextWebInformation object that specifies metadata about the site."""
        return self.pending_request().context_info

    @property
    def web(self) -> Web:
        """
        A group of related webpages that is hosted by a server on the World Wide Web or an intranet.
        Each website has its own entry points, metadata, administration settings, and workflows.
        """
        if not self._web:
            self._web = Web(self)
        return self._web

    @property
    def site(self) -> Site:
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
    def announcements(self):
        """Announcements controller"""
        from office365.sharepoint.publishing.announcements.controller import (
            AnnouncementsController,
        )

        return AnnouncementsController(self, ResourcePath("Announcements"))

    @property
    def brand_center(self) -> BrandCenter:
        """Alias to BrandCenter"""

        from office365.sharepoint.brandcenter.brand_center import BrandCenter

        return BrandCenter(self)

    @property
    def client_people_picker(self):
        """Query principals service alias"""

        from office365.sharepoint.ui.applicationpages.peoplepicker.web_service_interface import (
            ClientPeoplePickerWebServiceInterface,
        )

        return ClientPeoplePickerWebServiceInterface(self)

    @property
    def component_context_info(self):
        """ComponentContextInfo alias"""

        from office365.sharepoint.clientsidecomponent.component_context_info import (
            ComponentContextInfo,
        )

        return ComponentContextInfo(self, ResourcePath("ComponentContextInfo"))

    @property
    def consumer_permissions(self):
        """Consumer permissions alias"""
        from office365.sharepoint.convergence.consumer_permissions import (
            ConsumerPermissions,
        )

        return ConsumerPermissions(self, ResourcePath("ConsumerPermissions"))

    @property
    def document_id(self):
        """Document IDs service"""

        from office365.sharepoint.documentmanagement.document_id import DocumentId

        return DocumentId(self)

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
    def directory_provider(self):
        """Alias to SharePointDirectoryProvider"""
        from office365.sharepoint.directory.provider.provider import (
            SharePointDirectoryProvider,
        )

        return SharePointDirectoryProvider(self)

    @property
    def employee_experience(self):
        """Alias to EmployeeExperience"""
        from office365.sharepoint.viva.employee_experience_controller import (
            EmployeeExperienceController,
        )

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
        from office365.sharepoint.contentcenter.machinelearning.models.collection import (
            SPMachineLearningModelCollection,
        )

        return SPMachineLearningModelCollection(self, ResourcePath("models"))

    @property
    def folder_coloring(self):
        """Alias to FolderColoring"""
        from office365.sharepoint.folders.coloring import FolderColoring

        return FolderColoring(self, ResourcePath("foldercoloring"))

    @property
    def font_packages(self):
        """Alias to FontPackageCollection"""

        from office365.sharepoint.fontpackages.collection import FontPackageCollection

        return FontPackageCollection(self, ResourcePath("fontpackages"))

    @property
    def site_font_packages(self):
        """Alias to FontPackageCollection"""

        from office365.sharepoint.fontpackages.collection import FontPackageCollection

        return FontPackageCollection(self, ResourcePath("sitefontpackages"))

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
        from office365.sharepoint.navigation.service import NavigationService

        return NavigationService(self)

    @property
    def page_diagnostics(self):
        """Alias to PageDiagnosticsController"""
        from office365.sharepoint.publishing.diagnostics.controller import (
            PageDiagnosticsController,
        )

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
    def document_crawl_log(self):
        """Alias to DocumentCrawlLog"""

        from office365.sharepoint.search.administration.document_crawl_log import (
            DocumentCrawlLog,
        )

        return DocumentCrawlLog(self)

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
        from office365.sharepoint.contentcenter.machinelearning.hub import (
            SPMachineLearningHub,
        )

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
        """Alias to Microsoft.SharePoint.Portal.SiteIconManager."""
        from office365.sharepoint.portal.sites.icon_manager import SiteIconManager

        return SiteIconManager(self, ResourcePath("SiteIconManager"))

    @property
    def site_linking_manager(self):
        """Alias to Microsoft.SharePoint.Portal.SiteLinkingManager."""
        from office365.sharepoint.portal.linkedsites.manager import SiteLinkingManager

        return SiteLinkingManager(self, ResourcePath("siteLinkingManager"))

    @property
    def site_manager(self):
        """Alias to SPSiteManager. Represents methods for creating and managing SharePoint sites"""
        from office365.sharepoint.portal.sites.manager import SPSiteManager

        return SPSiteManager(self, ResourcePath("spSiteManager"))

    @property
    def site_manager_svc(self):
        """Alias to SiteManagerService."""

        from office365.sharepoint.sites.manager.service import SiteManagerService

        return SiteManagerService(self)

    @property
    def social_feed_manager(self):
        """Alias to SocialFeedManager."""
        from office365.sharepoint.social.feed.manager import SocialFeedManager

        return SocialFeedManager(self)

    @property
    def home_service(self):
        """Alias to SharePointHomeServiceContextBuilder."""
        from office365.sharepoint.portal.home.service_context_builder import (
            SharePointHomeServiceContextBuilder,
        )

        return SharePointHomeServiceContextBuilder(self, ResourcePath("sphomeservice"))

    @property
    def home_site(self):
        """Alias to SPHSite."""
        from office365.sharepoint.sites.home.site import SPHSite

        return SPHSite(self, ResourcePath("SPHSite"))

    @property
    def people_picker(self) -> PeoplePickerWebServiceInterface:
        """Query principals service alias"""

        return PeoplePickerWebServiceInterface(self)

    @property
    def publications(self):
        from office365.sharepoint.contentcenter.machinelearning.publications.publication import (
            SPMachineLearningPublication,
        )
        from office365.sharepoint.entity_collection import EntityCollection

        return EntityCollection(self, SPMachineLearningPublication, ResourcePath("publications"))

    @property
    def server_settings(self) -> ServerSettings:
        """Provides methods for obtaining server properties"""

        from office365.sharepoint.server_settings import ServerSettings

        return ServerSettings(self)

    @property
    def social_following_manager(self):
        """ """
        from office365.sharepoint.social.following.manager import SocialFollowingManager

        return SocialFollowingManager(self)

    @property
    def theme_manager(self) -> ThemeManager:
        """Alias to SP.Utilities.ThemeManager. Represents methods for creating and managing site theming"""
        from office365.sharepoint.portal.theme_manager import ThemeManager

        return ThemeManager(self, ResourcePath("themeManager"))

    @property
    def taxonomy(self):
        """Alias to TaxonomyService"""
        from office365.sharepoint.taxonomy.service import TaxonomyService

        return TaxonomyService(self)

    @property
    def search(self) -> SearchService:
        """Alias to SearchService"""
        from office365.sharepoint.search.service import SearchService

        return SearchService(self)

    @property
    def tenant_settings(self) -> TenantSettings:
        """Alias to TenantSettings"""
        from office365.sharepoint.tenant.settings import TenantSettings

        return TenantSettings.current(self)

    @property
    def viva_site_manager(self) -> VivaSiteManager:
        """"""
        from office365.sharepoint.viva.site_manager import VivaSiteManager

        return VivaSiteManager(self)

    @property
    def workflow_services_manager(self):
        """Alias to WorkflowServicesManager"""
        from office365.sharepoint.workflow.servicesmanager import (
            WorkflowServicesManager,
        )

        return WorkflowServicesManager.current(self)

    @property
    def workflow_deployment_service(self):
        """Alias to WorkflowServicesManager"""

        from office365.sharepoint.workflow.deployment_service import (
            WorkflowDeploymentService,
        )

        return WorkflowDeploymentService(self)

    @property
    def work_items(self):
        """"""
        from office365.sharepoint.contentcenter.machinelearning.workitems.collection import (
            SPMachineLearningWorkItemCollection,
        )

        return SPMachineLearningWorkItemCollection(self, ResourcePath("workitems"))

    @property
    def tenant(self) -> Tenant:
        from office365.sharepoint.tenant.administration.tenant import Tenant

        if self.is_tenant:
            return Tenant(self)
        else:
            admin_ctx = self.clone(self.tenant_url, False)
            return Tenant(admin_ctx)

    @property
    def tenant_url(self) -> str:
        root_url = get_absolute_url(self.base_url)
        if "-admin." in root_url:
            return root_url
        result = urlparse(self.base_url)
        names = str(result.netloc).split(".")
        names[0] = names[0] + "-admin"
        return result.scheme + "://" + ".".join(names)

    @property
    def site_path(self) -> str:
        root_url = get_absolute_url(self.base_url)
        return self.base_url.replace(root_url, "")

    @property
    def is_tenant(self) -> bool:
        """
        Determines whether the current site is a tenant administration site
        """
        return self.tenant_url == self.base_url

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def authentication_context(self) -> AuthenticationContext:
        return self.pending_request().authentication_context
