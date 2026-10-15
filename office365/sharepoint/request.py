from __future__ import annotations

import threading
from typing import Callable, List, Optional, Union

from requests import Response
from typing_extensions import Self

from office365.azure_env import AzureEnvironment
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.auth.certificate import CertificateData
from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.auth.token_response import TokenResponse
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.client_request import ASYNC_AUTHENTICATED_FLAG
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.http.url import get_absolute_url
from office365.runtime.odata.json_format import ODataJsonFormat
from office365.runtime.odata.request import ODataRequest
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.delete_entity import DeleteEntityQuery
from office365.runtime.queries.update_entity import UpdateEntityQuery
from office365.runtime.transport.offload import run_offloaded
from office365.sharepoint.exceptions import SecurityValidationException
from office365.sharepoint.webs.context_web_information import ContextWebInformation


class SharePointRequest(ODataRequest):
    """Client request for SharePoint REST API


    Typical usage:
        >>> request = SharePointRequest("https://contoso.sharepoint.com")
        >>> response = request.execute_request("web/currentUser")
        >>> json = json.loads(response.content)
        >>> prop_val = json["d"]["UserPrincipalName"]
    """

    def __init__(
        self,
        base_url: str,
        environment: AzureEnvironment = AzureEnvironment.Global,
        allow_ntlm: bool = False,
        browser_mode: bool = False,
        authority: Optional[str] = None,
        json_format: Optional[ODataJsonFormat] = None,
    ):
        """
        Initialize SharePoint request client

        Args:
            base_url: Absolute Web or Site URL
            environment: Office 365 Cloud Environment endpoint (default: AzureEnvironment.Global)
            allow_ntlm: Whether NTLM authentication is enabled (default: False)
            browser_mode: Enable browser authentication (default: False)
            authority: Override the MSAL authority URL (e.g. https://<tenant>.ciamlogin.com)
            json_format: Response JSON format (default: V3 JsonLightFormat; pass a V4
              format for the ``_api/v2.1`` OData V4 endpoints)
        """
        super().__init__(base_url, json_format or JsonLightFormat())
        self._auth_context = AuthenticationContext(
            url=base_url,
            environment=environment,
            allow_ntlm=allow_ntlm,
            browser_mode=browser_mode,
            authority=authority,
        )
        self._ctx_web_info: ContextWebInformation | None = None
        self._digest_lock = threading.Lock()
        self.beforeExecute += self._authenticate_request
        self.beforeExecute += self.ensure_form_digest
        self._async_authenticate = self._authenticate_request_async

    def _authenticate_request(self, request: RequestOptions) -> None:
        """Authenticate the request, resolving the auth context lazily so it can be
        swapped via :meth:`reuse`.

        A transport carrying its own handler (``session.auth``, e.g. ``HttpNtlmAuth``)
        signs the request itself. Such a session counts as credentials when no
        provider is configured on the auth context.
        """
        if getattr(request, ASYNC_AUTHENTICATED_FLAG, False):
            return  # already authenticated by :meth:`_authenticate_request_async`
        if not self._auth_context.is_configured and self._transport.auth is not None:
            return
        self._auth_context.authenticate_request(request)

    async def _authenticate_request_async(self, request: RequestOptions) -> None:
        """Authenticate the request on the event loop when the token callback is async.

        Synchronous providers are handled by the offloaded
        :meth:`_authenticate_request` hook instead.
        """
        if not self._auth_context.is_async_token_callback:
            return
        await self._auth_context.authenticate_request_async(request)
        setattr(request, ASYNC_AUTHENTICATED_FLAG, True)

    def set_base_url(self, url: str) -> Self:
        self._base_url = url
        self._auth_context.url = url
        return self

    def reuse(self, other: SharePointRequest) -> Self:
        """Reuse the authentication context and transport of another request.

        The same objects are shared by reference (not copied), so the token
        cache and HTTP session stay single-flight and thread-safe. An explicit
        async transport (see ``with_async_transport``), the shared rate
        limiter and the client-level retry policy are carried over as well, so
        clones keep using the same native-async engine, fleet-wide pacing and
        resilience policy.

        Args:
            other: The request whose auth context and transport to reuse
        """
        self._auth_context = other._auth_context
        self._transport = other._transport
        self._async_transport = other._async_transport
        self._rate_limiter = other._rate_limiter
        self._retry_policy = other._retry_policy
        return self

    def build_request(self, query: ClientQuery) -> RequestOptions:
        request = super().build_request(query)
        if isinstance(self.json_format, JsonLightFormat):
            if isinstance(query, DeleteEntityQuery):
                request.ensure_header("X-HTTP-Method", "DELETE")
                request.ensure_header("IF-MATCH", "*")
            elif isinstance(query, UpdateEntityQuery):
                request.ensure_header("X-HTTP-Method", "MERGE")
                request.ensure_header("IF-MATCH", "*")
        return request

    def _fetch_context_web_information(self) -> ContextWebInformation:
        """Fetches the form digest (``/_api/contextInfo``), retrying throttling.

        A throttled digest refresh would otherwise abort the whole run; retry
        transient failures honoring the server's ``Retry-After``.
        """
        from office365.runtime.retry import response_retry_after, retry

        def _attempt() -> ContextWebInformation:
            client = ODataRequest(self._base_url, JsonLightFormat())
            client._transport = self._transport
            client.beforeExecute += self._authenticate_request
            request = RequestOptions(f"{self.service_root_url}/contextInfo")
            request.method = HttpMethod.Post
            response = client.execute_request_direct(request)
            json_format = JsonLightFormat()
            json_format.function = "GetContextWebInformation"
            return_value = ContextWebInformation()
            client.map_json(response.json(), return_value, json_format)
            return return_value

        return retry(
            _attempt,
            on_failure=lambda _attempt_num, ex: response_retry_after(getattr(ex, "response", None)),
        )

    def _ensure_digest(self) -> None:
        """Single-flight fetch of a valid form digest."""
        if not self.context_info.is_valid:
            with self._digest_lock:
                if not self.context_info.is_valid:
                    self._ctx_web_info = self._fetch_context_web_information()

    def warm_up(self) -> None:
        """Fetch the form digest once (e.g. before dispatching parallel batches)."""
        self._ensure_digest()

    async def warm_up_async(self) -> None:
        """Async twin of :meth:`warm_up`: fetch the digest without blocking the loop.

        The digest fetch uses blocking HTTP, so it is offloaded to a worker
        thread while the event loop stays free. When the token callback is async,
        the access token is acquired first so the (blocking) digest request can
        reuse the cached token through the synchronous auth hook.
        """
        await self._auth_context.acquire_token_async()
        await run_offloaded(self.warm_up)

    def invalidate_digest(self) -> None:
        """Drop the cached digest so the next request re-fetches it."""
        with self._digest_lock:
            self._ctx_web_info = None

    def ensure_form_digest(self, request: RequestOptions) -> None:
        self._ensure_digest()
        assert self._ctx_web_info is not None
        request.set_header("X-RequestDigest", self._ctx_web_info.FormDigestValue)

    def execute_request_direct(self, request: RequestOptions) -> Response:
        """Send a request, recovering once from an expired/invalidated form digest."""
        try:
            return super().execute_request_direct(request)
        except SecurityValidationException:
            self.invalidate_digest()
            return super().execute_request_direct(request)

    @property
    def context_info(self) -> ContextWebInformation:
        """Returns a ContextWebInformation object that specifies metadata about the site."""
        if self._ctx_web_info is None:
            self._ctx_web_info = ContextWebInformation()
        return self._ctx_web_info

    def execute_request(self, path: str) -> Response:
        """
        Execute direct request to SharePoint REST endpoint

        Args:
            path: Relative API path

        Returns:
            HTTP response
        """
        request_url = f"{self.service_root_url}/{path}"
        return self.execute_request_direct(RequestOptions(request_url))

    def with_credentials(self, credentials: Union[UserCredential, ClientCredential]) -> Self:
        """
        Initialize authentication with user or client credentials

        Args:
            credentials: Authentication credentials

        Returns:
            Self: Supports method chaining
        """
        self._auth_context.with_credentials(credentials)
        return self

    def with_cookies(self, cookie_source, ttl_seconds: int | None = None):
        """Initializes authentication using browser-session cookies.

        Args:
            cookie_source (object): Callable returning Dict[str, str] or an AuthCookies instance.
            ttl_seconds (object): Optional max age for cached cookies before reloading from source.
        """
        self._auth_context.with_cookies(cookie_source, ttl_seconds)
        return self

    def with_client_secret(
        self, tenant: str, client_id: str, client_secret: str, scopes: Optional[List[str]] = None
    ) -> Self:
        """Authenticate using client secret (MSAL app-only).

        Args:
            tenant: Tenant name
            client_id: Application client ID
            client_secret: Client secret value
            scopes: Requested permission scopes (optional)

        Returns:
            Self: Supports method chaining
        """
        self._auth_context.with_client_secret(tenant, client_id, client_secret, scopes)
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
        """
        Authenticate using client certificate

        Args:
            tenant: Tenant name
            client_id: Application client ID
            thumbprint: Certificate thumbprint (optional when ``public_certificate`` is given)
            cert_path: Path to PEM encoded private key (optional)
            private_key: PEM encoded private key (optional)
            scopes: Requested permission scopes (optional)
            passphrase: Private key passphrase (optional)
            public_certificate: Certificate (DER/PEM bytes, inline PEM text, or a
                path) used to derive the thumbprint or, with ``use_sni``, for
                subject name/issuer authentication (optional)
            use_sni: Use subject name/issuer authentication (requires the optional
                ``cryptography`` package)

        Returns:
            Self: Supports method chaining
        """
        self._auth_context.with_client_certificate(
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

    def with_device_flow(self, tenant: str, client_id: str, scopes: Optional[List[str]] = None) -> Self:
        """
        Authenticate using device flow

        Args:
            tenant: Tenant name
            client_id: Application client ID
            scopes: Requested permission scopes (optional)

        Returns:
            Self: Supports method chaining
        """
        self._auth_context.with_device_flow(tenant, client_id, scopes)
        return self

    def with_username_and_password(
        self,
        tenant: str,
        client_id: str,
        username: str,
        password: str,
        scopes: Optional[list[str]] = None,
    ) -> Self:
        """Initialize with username/password authentication (MSAL ROPC flow).

        Args:
            tenant: Tenant name or identifier, e.g. "contoso.onmicrosoft.com"
            client_id: The OAuth client ID of the calling application
            username: Typically a UPN in the form of an email address
            password: The password
            scopes: Scopes requested to access a protected API (a resource)
        """
        if scopes is None:
            resource = get_absolute_url(self.base_url)
            scopes = [f"{resource}/.default"]
        self._auth_context.with_username_and_password(tenant, client_id, username, password, scopes)
        return self

    def with_interactive(self, tenant: str, client_id: str, scopes: Optional[List[str]] = None) -> Self:
        """
        Authenticate interactively via browser

        Args:
            tenant: Tenant name
            client_id: Application client ID
            scopes: Requested permission scopes (optional)

        Returns:
            Self: Supports method chaining
        """
        self._auth_context.with_interactive(tenant, client_id, scopes)
        return self

    def with_access_token(self, token_func: Callable[[], TokenResponse]) -> Self:
        """
        Initialize with token callback function

        Args:
            token_func: Function that returns a token response

        Returns:
            Self: Supports method chaining
        """
        self._auth_context.with_access_token(token_func)
        return self

    @property
    def authentication_context(self) -> AuthenticationContext:
        """Get the authentication context"""
        return self._auth_context

    @property
    def base_url(self) -> str:
        """Represents Base Url"""
        return self._base_url

    @property
    def service_root_url(self) -> str:
        """Get the SharePoint REST API service root URL

        Routing is derived from this request's own base URL, not from the
        authentication context. :meth:`reuse` shares the auth context by
        reference (so clones keep the same token cache and transport), which
        means ``authentication_context.url`` still points at the *source* site
        after a cross-site :meth:`ClientContext.clone`. Using it here would
        route every cloned request back to the source site.
        """
        return f"{self._base_url}/_api"
