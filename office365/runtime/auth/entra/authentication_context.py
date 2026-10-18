from __future__ import annotations

import asyncio
import inspect
import sys
import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional

from typing_extensions import Self

from office365.azure_env import (
    AzureEnvironment,
    get_graph_authority,
    get_login_authority,
)
from office365.runtime.auth.certificate import CertificateData, build_client_credential
from office365.runtime.auth.token_response import TokenResponse
from office365.runtime.transport.offload import run_offloaded

#: Fallback lifetime for an async-acquired token whose response carries no
#: ``expiresIn``. It only needs to outlive the batch payload build that reuses it.
_DEFAULT_TOKEN_TTL = 300


class AuthenticationContext:
    """Provides authentication context for Microsoft Graph client"""

    def __init__(
        self,
        tenant: str | None = None,
        scopes: List[str] | None = None,
        token_cache: Any = None,
        environment: AzureEnvironment = AzureEnvironment.Global,
        authority: str | None = None,
    ):
        """Args:
        tenant (str): Tenant name, for example: contoso.onmicrosoft.com
        scopes (list[str] or None): Scopes requested to access an API
        token_cache (Any): Default cache is in memory only, Refer https://msal-python.readthedocs.io/en/latest/#msal.SerializableTokenCache
        authority (str or None): Override the MSAL authority URL, e.g. for Entra External ID (CIAM):
            https://<tenant>.ciamlogin.com
        """
        self._tenant = tenant
        if scopes is None:
            scopes = [f"{get_graph_authority(environment)}/.default"]
        self._scopes = scopes
        self._token_cache = token_cache
        self._token_callback: Any = None
        self._environment = environment
        self._client_id: str | None = None
        self._authority = authority
        self._lock = threading.Lock()
        self._token_callback_is_async = False
        self._async_lock: Optional[asyncio.Lock] = None
        self._async_lock_loop: Any = None
        self._cached_token: Optional[TokenResponse] = None
        self._token_expires = datetime.now(timezone.utc)

    def acquire_token(self) -> TokenResponse:
        """Acquire access token (single-flight under concurrent batches).

        When the callback registered via :meth:`with_access_token` is a coroutine
        function, the token is only available on the async API; this returns the
        token cached by :meth:`acquire_token_async` while it is still valid (so
        synchronous batch payload building can reuse it) and otherwise raises.
        """
        if not self._token_callback:
            raise ValueError("Token callback is not set.")
        if self._token_callback_is_async:
            cached = self._get_cached_token()
            if cached is not None:
                return cached
            raise RuntimeError(
                "An async token callback requires the async API; await "
                "execute_query_async() / execute_batch_async() instead."
            )
        with self._lock:
            token_resp = self._token_callback()
        token = TokenResponse.from_json(token_resp)
        return token

    async def acquire_token_async(self) -> TokenResponse:
        """Acquire access token without blocking the event loop.

        Async counterpart of :meth:`acquire_token`. A callback registered via
        :meth:`with_access_token` that is a coroutine function is awaited on the
        loop, so token acquisition can use genuinely asynchronous I/O (for
        example an async secret store or metadata endpoint). Concurrent awaiters
        share one acquisition under an :class:`asyncio.Lock`, and the token is
        briefly cached so the synchronous ``beforeExecute`` hooks used to build a
        batch payload can reuse it. A synchronous callback is offloaded to the
        worker pool.
        """
        if self._token_callback is None:
            raise ValueError("Token callback is not set.")
        if self._token_callback_is_async:
            cached = self._get_cached_token()
            if cached is not None:
                return cached
            async with self._get_async_lock():
                cached = self._get_cached_token()
                if cached is not None:
                    return cached
                token = TokenResponse.from_json(await self._token_callback())
                self._store_cached_token(token)
                return token
        token_resp = await run_offloaded(self._token_callback)
        return TokenResponse.from_json(token_resp)

    def _get_cached_token(self) -> Optional[TokenResponse]:
        if self._cached_token is not None and datetime.now(timezone.utc) <= self._token_expires:
            return self._cached_token
        return None

    def _store_cached_token(self, token: TokenResponse) -> None:
        self._cached_token = token
        expires_in = getattr(token, "expiresIn", None)
        ttl = int(expires_in) if expires_in is not None else _DEFAULT_TOKEN_TTL
        self._token_expires = datetime.now(timezone.utc) + timedelta(seconds=ttl)

    def _get_async_lock(self) -> asyncio.Lock:
        """Return a lock for the running loop, recreating it when the loop changes.

        A lock binds to the loop that first waits on it, so a lock kept across
        two ``asyncio.run()`` calls can fail with ``Event loop is closed`` (or
        hang) once it is contended. The lock exists only to collapse concurrent
        acquisitions, so replacing it for a new loop costs nothing.
        """
        loop = asyncio.get_running_loop()
        if self._async_lock is None or self._async_lock_loop is not loop:
            self._async_lock = asyncio.Lock()
            self._async_lock_loop = loop
        return self._async_lock

    @property
    def is_async_token_callback(self) -> bool:
        """Whether the registered token callback is a coroutine function."""
        return self._token_callback_is_async

    def with_access_token(self, token_callback: Callable[[], Optional[Dict[str, Any]]]) -> Self:
        """Register a token callback.

        The callback may be a regular function (offloaded by the async engine) or
        an ``async def`` coroutine function, which the async API awaits directly
        (see :meth:`acquire_token_async`). Async callbacks are only supported on
        the async API; a synchronous request with one raises a clear error.
        """
        self._token_callback = token_callback
        self._token_callback_is_async = inspect.iscoroutinefunction(token_callback)
        self._cached_token = None
        self._token_expires = datetime.now(timezone.utc)
        return self

    def with_device_flow(self, client_id: str) -> Self:
        """Initializes the client via device code flow.

        Useful for CLI tools and headless environments. The user authenticates
        by visiting a URL on another device and entering the displayed code.

        Args:
            client_id: The OAuth client id of the calling application.
        """
        self._client_id = client_id
        import msal

        app = msal.PublicClientApplication(client_id, authority=self.authority_url)

        def _acquire_token():
            # Reuse the signed-in account so only the first request shows a code;
            # MSAL refreshes the access token in the background when needed.
            accounts = app.get_accounts()
            if accounts:
                result = app.acquire_token_silent(self._scopes, account=accounts[0])
                if result:
                    return result
            flow = app.initiate_device_flow(scopes=self._scopes)
            if "user_code" not in flow:
                raise ValueError(f"Failed to create device flow: {flow}")
            print(flow["message"])
            sys.stdout.flush()
            return app.acquire_token_by_device_flow(flow)

        return self.with_access_token(_acquire_token)

    def with_certificate(
        self,
        client_id: str,
        thumbprint: str | None = None,
        private_key: str | None = None,
        *,
        public_certificate: CertificateData | None = None,
        passphrase: str | None = None,
        use_sni: bool = False,
    ):
        """Initializes the confidential client with client certificate

        Args:
            client_id (str): The OAuth client id of the calling application.
            thumbprint (str): Thumbprint (optional when ``public_certificate`` is given)
            private_key (str): Private key
            public_certificate: Certificate (DER/PEM bytes, inline PEM text, or a
                path) used to derive the thumbprint or, with ``use_sni``, for
                subject name/issuer authentication
            passphrase (str): Private key passphrase
            use_sni (bool): Use subject name/issuer authentication (requires the
                optional ``cryptography`` package)
        """
        self._client_id = client_id
        import msal

        credentials = build_client_credential(
            thumbprint=thumbprint,
            private_key=private_key,
            public_certificate=public_certificate,
            passphrase=passphrase,
            use_sni=use_sni,
        )
        app = msal.ConfidentialClientApplication(
            client_id,
            authority=self.authority_url,
            client_credential=credentials,
            token_cache=self._token_cache,  # Default cache is in memory only.
            # You can learn how to use SerializableTokenCache from
            # https://msal-python.readthedocs.io/en/latest/#msal.SerializableTokenCache
        )

        def _acquire_token():
            return app.acquire_token_for_client(scopes=self._scopes)

        return self.with_access_token(_acquire_token)

    def with_client_secret(self, client_id: str, client_secret: str) -> Self:
        """Initializes the confidential client with client secret

        Args:
            client_id (str): The OAuth client id of the calling application.
            client_secret (str): Client secret
        """
        self._client_id = client_id
        import msal

        app = msal.ConfidentialClientApplication(
            client_id,
            authority=self.authority_url,
            client_credential=client_secret,
            token_cache=self._token_cache,
        )

        def _acquire_token():
            return app.acquire_token_for_client(scopes=self._scopes)

        return self.with_access_token(_acquire_token)

    def with_token_interactive(self, client_id: str, username: Optional[str] = None) -> Self:
        """Initializes the client via user credentials
        Note: only works if your app is registered with redirect_uri as http://localhost

        Args:
            client_id (str): The OAuth client id of the calling application.
            username (str): Typically a UPN in the form of an email address.
        """
        self._client_id = client_id
        import msal

        app = msal.PublicClientApplication(client_id, authority=self.authority_url)

        def _acquire_token():
            # The pattern to acquire a token looks like this.
            result = None

            # Firstly, check the cache to see if this end user has signed in before
            accounts = app.get_accounts(username=username)
            if accounts:
                chosen = accounts[0]  # Assuming the end user chose this one to proceed
                # Now let's try to find a token in cache for this account
                result = app.acquire_token_silent(self._scopes, account=chosen)

            if not result:
                result = app.acquire_token_interactive(
                    self._scopes,
                    login_hint=username,
                )
            return result

        return self.with_access_token(_acquire_token)

    def with_username_and_password(self, client_id: str, username: str, password: str) -> Self:
        """Initializes the client via user credentials

        Args:
            client_id (str): The OAuth client id of the calling application.
            username (str): Typically a UPN in the form of an email address.
            password (str): The password.
        """
        self._client_id = client_id
        import msal

        app = msal.PublicClientApplication(
            authority=self.authority_url,
            client_id=client_id,
        )

        def _acquire_token():
            result = None
            accounts = app.get_accounts(username=username)
            if accounts:
                result = app.acquire_token_silent(self._scopes, account=accounts[0])

            if not result:
                result = app.acquire_token_by_username_password(
                    username=username,
                    password=password,
                    scopes=self._scopes,
                )
            return result

        return self.with_access_token(_acquire_token)

    @property
    def client_id(self) -> str | None:
        """The application (client) ID used for authentication."""
        return self._client_id

    @property
    def authority_url(self) -> str:
        if self._authority is not None:
            return self._authority
        return f"{get_login_authority(self._environment)}/{self._tenant}"

    def with_authority(self, authority: str) -> Self:
        """Override the MSAL authority URL, e.g. for Entra External ID (CIAM) tenants:

            https://<tenant>.ciamlogin.com

        Args:
            authority: Full authority URL used by all subsequent token acquisitions
        """
        self._authority = authority
        return self
