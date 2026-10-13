from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from typing_extensions import Self

from office365.admin.admin import Admin
from office365.azure_env import AzureEnvironment
from office365.booking.solutions.root import SolutionsRoot
from office365.communications.cloud_communications import CloudCommunications
from office365.copilot.root import CopilotRoot
from office365.delta_collection import DeltaCollection
from office365.directory.applications.collection import ApplicationCollection
from office365.directory.applications.template import ApplicationTemplate
from office365.directory.audit.log_root import AuditLogRoot
from office365.directory.authentication.methods.configuration import (
    AuthenticationMethodConfiguration,
)
from office365.directory.certificates.auth_configuration import (
    CertificateBasedAuthConfiguration,
)
from office365.directory.directory import Directory
from office365.directory.domains.collection import DomainCollection
from office365.directory.extensions.schema import SchemaExtension
from office365.directory.groups.collection import GroupCollection
from office365.directory.groups.lifecycle_policy import GroupLifecyclePolicy
from office365.directory.groups.setting_template import GroupSettingTemplate
from office365.directory.identities.container import IdentityContainer
from office365.directory.identities.provider import IdentityProvider
from office365.directory.identitygovernance.governance import IdentityGovernance
from office365.directory.internal.paths.me import MePath
from office365.directory.invitations.collection import InvitationCollection
from office365.directory.licenses.collection import SubscribedSkuCollection
from office365.directory.objects.collection import DirectoryObjectCollection
from office365.directory.permissions.grants.oauth2_collection import OAuth2PermissionGrantCollection
from office365.directory.permissions.grants.resource_specific import (
    ResourceSpecificPermissionGrant,
)
from office365.directory.policies.root import PolicyRoot
from office365.directory.protection.information import InformationProtection
from office365.directory.protection.root import IdentityProtectionRoot
from office365.directory.rolemanagement.management import RoleManagement
from office365.directory.rolemanagement.roles.collection import DirectoryRoleCollection
from office365.directory.serviceprincipals.collection import ServicePrincipalCollection
from office365.directory.tenantinformation.relationship import TenantRelationship
from office365.directory.users.collection import UserCollection
from office365.directory.users.user import User
from office365.education.root import EducationRoot
from office365.entity_collection import EntityCollection
from office365.graph_request import GraphRequest
from office365.intune.devices.collection import DeviceCollection
from office365.intune.devices.management.app_management import DeviceAppManagement
from office365.intune.devices.management.management import DeviceManagement
from office365.intune.organizations.contact import OrgContact
from office365.intune.organizations.organization import Organization
from office365.intune.print.print import Print
from office365.onedrive.drives.collection import DriveCollection
from office365.onedrive.shares.collection import SharesCollection
from office365.onedrive.sites.sites_with_root import SitesWithRoot
from office365.onedrive.storage.storage import Storage
from office365.outlook.calendar.place_collection import PlaceCollection
from office365.outlook.calendar.rooms.list import RoomList
from office365.planner.planner import Planner
from office365.reports.root import ReportRoot
from office365.runtime.auth.certificate import CertificateData
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.v4.batch_request import DEFAULT_MAX_BATCH_BYTES, ODataV4BatchRequest
from office365.runtime.odata.v4.json_format import V4JsonFormat
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.transport.base import NoTimeoutType
from office365.runtime.transport.requests_transport import DEFAULT_POOL_CONNECTIONS, DEFAULT_POOL_MAXSIZE
from office365.search.entity import SearchEntity
from office365.search.external.connection import ExternalConnection
from office365.search.external.external import External
from office365.security.security import Security
from office365.subscriptions.collection import SubscriptionCollection
from office365.teams.apps.catalog import AppCatalogs
from office365.teams.chats.collection import ChatCollection
from office365.teams.collection import TeamCollection
from office365.teams.template import TeamsTemplate
from office365.teams.viva.employee_experience import EmployeeExperience
from office365.teams.work import Teamwork

if TYPE_CHECKING:
    from requests import Session

    from office365.directory.applications.roles.collection import AppRoleCollection
    from office365.directory.applications.roles.role import AppRole
    from office365.directory.groups.setting import GroupSetting
    from office365.directory.rolemanagement.templates.collection import DirectoryRoleTemplateCollection
    from office365.runtime.client_result import ClientResult
    from office365.runtime.queries.batch import BatchQuery
    from office365.runtime.types.collections import StringCollection


class GraphClient(ClientRuntimeContext):
    """Microsoft Graph API client"""

    def __init__(
        self,
        token_callback: Optional[Callable[[], Dict[str, str]]] = None,
        tenant: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        token_cache: Any = None,
        environment: AzureEnvironment = AzureEnvironment.Global,
        authority: Optional[str] = None,
    ):
        """
        Initialize Microsoft Graph client

        Args:
            token_callback: Optional token callback function
            tenant: Tenant ID or domain name
            scopes: List of permission scopes
            token_cache: Token cache implementation. Refer
                https://msal-python.readthedocs.io/en/latest/#msal.SerializableTokenCache
            environment: Azure environment (default: AzureEnvironment.Global)
            authority: Override the MSAL authority URL (e.g. https://<tenant>.ciamlogin.com)
        """

        super().__init__()
        self._token_callback = token_callback
        self._tenant = tenant
        self._token_cache = token_cache
        self._environment = environment
        self._scopes = scopes
        self._directory: Optional[Directory] = None
        self._authority = authority

    def with_certificate(
        self,
        client_id: str,
        thumbprint: str | None = None,
        private_key: str | None = None,
        *,
        public_certificate: CertificateData | None = None,
        passphrase: str | None = None,
        use_sni: bool = False,
    ) -> Self:
        """
        Initialize with client certificate authentication

        Args:
            client_id: Application client ID
            thumbprint: Certificate thumbprint (optional when ``public_certificate`` is given)
            private_key: Private key content
            public_certificate: Certificate (DER/PEM bytes, inline PEM text, or a
                path) used to derive the thumbprint or, with ``use_sni``, for
                subject name/issuer authentication
            passphrase: Private key passphrase
            use_sni: Use subject name/issuer authentication (requires the optional
                ``cryptography`` package)

        Returns:
            self: Supports method chaining
        """
        self.pending_request().with_certificate(
            client_id,
            thumbprint,
            private_key,
            public_certificate=public_certificate,
            passphrase=passphrase,
            use_sni=use_sni,
        )
        return self

    def with_client_secret(self, client_id: str, client_secret: str) -> Self:
        """
        Initialize with client secret authentication

        Args:
            client_id: Application client ID
            client_secret: Client secret value

        Returns:
            self: Supports method chaining
        """
        self.pending_request().with_client_secret(client_id, client_secret)
        return self

    def with_token_interactive(self, client_id: str, username: Optional[str] = None) -> Self:
        """
        Initialize with interactive authentication flow

        Args:
            client_id: Application client ID
            username: Optional username for authentication
        """
        self.pending_request().with_token_interactive(client_id, username)
        return self

    def with_username_and_password(self, client_id: str, username: str, password: str) -> Self:
        """
        Initialize with username/password authentication

        Args:
            client_id: Application client ID
            username: User principal name
            password: User password
        """
        self.pending_request().with_username_and_password(client_id, username, password)
        return self

    def with_device_flow(self, client_id: str) -> Self:
        """
        Initialize with device code flow authentication.

        Useful for CLI tools and headless environments. The user authenticates
        by visiting a URL on another device and entering the displayed code.

        Args:
            client_id: Application client ID
        """
        self.pending_request().with_device_flow(client_id)
        return self

    def require_application_permission(self, *scopes: str) -> Self:
        """
        Exit if the application lacks at least one of the required Graph application permissions.

        Typical usage at the top of example scripts:

            client = (
                GraphClient(tenant=tenant)
                .with_client_secret(client_id, secret)
                .require_application_permission("DeviceManagementConfiguration.Read.All")
            )

            client = (
                GraphClient(tenant=tenant)
                .with_client_secret(client_id, secret)
                .require_application_permission("RoleManagement.Read.Directory", "Directory.Read.All")
            )

        Args:
            *scopes: Application permission names (e.g. "DeviceManagementConfiguration.Read.All");
                at least one must be granted to the app
        """
        from office365.runtime.client_request_exception import ClientRequestException

        if not scopes:
            return self
        client_id = self.pending_request().authentication_context.client_id
        try:
            assert client_id is not None
            result = self.get_application_permissions(client_id).execute_query()
            granted = {role.value for role in result.value}
            has_perms = any(scope in granted for scope in scopes)
            if not has_perms:
                print(f"Missing required application permission: need at least one of: {', '.join(scopes)}")
                sys.exit(1)
        except ClientRequestException:
            print(f"Could not verify permissions {scopes}: ensure Application.Read.All is granted.")
            sys.exit(1)
        return self

    def require_delegated_permission(self, *scopes: str) -> Self:
        """
        Exit if the application lacks at least one of the required Graph delegated permissions.

        Typical usage at the top of example scripts that call delegated APIs (e.g. ``/me``):

            client = (
                GraphClient(tenant=tenant)
                .with_username_and_password(client_id, username, password)
                .require_delegated_permission("User.Read")
            )

        Args:
            *scopes: Delegated permission names (e.g. "User.Read");
                at least one must be granted to the app
        """
        from office365.runtime.client_request_exception import ClientRequestException

        if not scopes:
            return self
        client_id = self.pending_request().authentication_context.client_id
        try:
            assert client_id is not None
            result = self.get_delegated_permissions(client_id).execute_query()
            granted = set(result.value)
            has_perms = any(scope in granted for scope in scopes)
            if not has_perms:
                print(f"Missing required delegated permission: need at least one of: {', '.join(scopes)}")
                sys.exit(1)
        except ClientRequestException:
            print(f"Could not verify permissions {scopes}: ensure Application.Read.All is granted.")
            sys.exit(1)
        return self

    def require_license(self, *keywords: str) -> Self:
        """Exit if the tenant has no subscribed SKU matching any of the given keywords.

        Typical usage at the top of example scripts that require a paid
        add-on license:

            client = (
                GraphClient(tenant=tenant)
                .with_client_secret(client_id, client_secret)
                .require_license("BACKUP")
            )

        Args:
            *keywords: Substrings to match against SKU part numbers
                (case-insensitive); at least one must match
        """
        if not keywords:
            return self
        skus = self.subscribed_skus.get().execute_query()
        matched = [
            s.sku_part_number
            for s in skus
            if s.sku_part_number and any(keyword.lower() in s.sku_part_number.lower() for keyword in keywords)
        ]
        if not matched:
            print(f"Missing required license: no subscribed SKU matches: {', '.join(keywords)}")
            sys.exit(1)
        return self

    def require_role(self, *role_names: str) -> Self:
        """
        Exit if the signed-in user lacks at least one of the required directory roles.

        Typical usage:

            client = (
                GraphClient(tenant=tenant)
                .with_token_interactive(client_id, admin_upn)
                .require_role("Global Administrator", "Privileged Role Administrator")
            )

        Args:
            *role_names: Directory role display names (e.g. "Global Administrator")
        """
        from office365.runtime.client_request_exception import ClientRequestException

        try:
            roles = self.me.get_directory_roles().execute_query()
            granted = {r.display_name for r in roles}
            if not any(role in granted for role in role_names):
                print(f"Need one of: {', '.join(role_names)}")
                sys.exit(1)
        except ClientRequestException:
            print("Could not verify roles — ensure RoleManagement.Read.Directory is granted.")
            sys.exit(1)
        return self

    def with_transport(
        self,
        proxies: dict[str, str] | None = None,
        verify: bool | str | None = None,
        timeout: float | tuple[float, float | None] | NoTimeoutType | None = None,
        session: Session | None = None,
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

    def with_throttle_priority(self, priority: str = "normal") -> Self:
        """Send ``x-ms-throttle-priority`` on every request (Graph throttling).

        Per Microsoft Graph, low-priority requests are throttled first and
        high-priority ones last; the header doesn't change the limits. Use
        ``"high"`` only for requests initiated by a user (where throttling causes
        user-visible failures) and ``"low"`` for background work.

        Args:
            priority: ``"low"``, ``"normal"`` (default) or ``"high"``.

        Raises:
            ValueError: When ``priority`` isn't one of the accepted values.
        """
        value = priority.lower()
        if value not in ("low", "normal", "high"):
            raise ValueError("priority must be one of 'low', 'normal', 'high'")

        def _set_header(request: RequestOptions) -> None:
            request.set_header("x-ms-throttle-priority", value)

        self.pending_request().before_execute(_set_header, once=False)
        return self

    def execute_batch(
        self,
        items_per_batch: int = 20,
        success_callback: Optional[Callable[[List[Any]], None]] = None,
        concurrency: int = 1,
        max_batch_bytes: Optional[int] = None,
        sequential: bool = False,
    ) -> Self:
        """
        Execute batched requests

        With ``concurrency`` > 1 the batches run on a thread pool; each batch
        is an independent HTTP request. Batches are capped by item count
        (``items_per_batch``) and by estimated payload size (``max_batch_bytes``).
        Throttled sub-requests (HTTP 429/503) are retried individually, honoring
        ``Retry-After`` — only the failed sub-requests are re-sent, so successful
        writes aren't re-applied. ``success_callback`` runs on the caller thread
        in completion order (not submission order).

        Pass ``sequential=True`` to chain the sub-requests with ``dependsOn`` so
        Graph runs them in order (a failed dependency yields HTTP 424). Use it
        only for **ordering-dependent side effects** — read-after-write on the
        same resource, delete-then-create, parent/child ordering — not for
        independent requests (Graph's default parallel mode is faster). A batch
        can't reference another sub-request's response, so it doesn't enable
        create-then-use-id flows. Implies ``concurrency=1`` because Graph only
        sequences within a single ``$batch``.

        Args:
            items_per_batch: Maximum items per batch (default: 20)
            success_callback: Optional callback for successful requests
            concurrency: Maximum number of concurrent batch requests (default 1)
            max_batch_bytes: Maximum estimated batch payload size (default ~3 MB)
            sequential: Chain sub-requests with ``dependsOn`` (Graph v4 only).

        Raises:
            ValueError: When ``sequential`` is combined with ``concurrency > 1``.
        """
        if sequential and concurrency > 1:
            raise ValueError("sequential=True requires concurrency=1 (Graph sequences within a batch only)")
        max_bytes = DEFAULT_MAX_BATCH_BYTES if max_batch_bytes is None else max_batch_bytes
        batches = self._split_batches(items_per_batch, max_bytes)
        if sequential:
            for batch in batches:
                batch.sequential = True
        if concurrency <= 1:
            batch_request = ODataV4BatchRequest("", V4JsonFormat())
            batch_request.beforeExecute += self.pending_request().authenticate_request
            for qry in batches:
                batch_request.execute_query_with_retry(qry)
                if callable(success_callback) and qry.return_types:
                    success_callback(qry.return_types)
            return self

        self.pending_request()
        self._execute_batches_in_parallel(batches, concurrency, success_callback)
        return self

    async def execute_batch_async(
        self,
        items_per_batch: int = 20,
        success_callback: Optional[Callable[[List[Any]], None]] = None,
        concurrency: int = 1,
        max_batch_bytes: Optional[int] = None,
        sequential: bool = False,
    ) -> Self:
        """Async counterpart of :meth:`execute_batch`.

        Pending queries are split exactly like the synchronous method, but each
        batch's HTTP round-trip runs off the event loop, so the loop is never
        blocked and independent batches overlap when ``concurrency`` > 1.
        ``sequential=True`` chains sub-requests with ``dependsOn`` just as the
        synchronous method does.

        Args:
            items_per_batch: Maximum items per batch (default: 20)
            success_callback: Optional callback for successful requests
            concurrency: Maximum number of concurrent batch requests (default 1)
            max_batch_bytes: Maximum estimated batch payload size (default ~3 MB)
            sequential: Chain sub-requests with ``dependsOn`` (Graph v4 only).

        Raises:
            ValueError: When ``sequential`` is combined with ``concurrency > 1``.
        """
        if sequential and concurrency > 1:
            raise ValueError("sequential=True requires concurrency=1 (Graph sequences within a batch only)")
        max_bytes = DEFAULT_MAX_BATCH_BYTES if max_batch_bytes is None else max_batch_bytes
        batches = self._split_batches(items_per_batch, max_bytes)
        if sequential:
            for batch in batches:
                batch.sequential = True
        self.pending_request()
        await self._run_batches_async(batches, concurrency, success_callback)
        return self

    def _execute_batch(self, batch_qry: "BatchQuery") -> list[Any]:
        """Execute a single batch unit on a worker thread (with per-request retry)."""
        batch_request = ODataV4BatchRequest("", V4JsonFormat())
        batch_request.beforeExecute += self.pending_request().authenticate_request
        batch_request.execute_query_with_retry(batch_qry)
        return batch_qry.return_types

    async def _execute_batch_async(self, batch_qry: "BatchQuery") -> list[Any]:
        """Execute a single batch unit through the async transport.

        Unlike the base implementation (which offloads the whole synchronous
        batch to a worker thread), this awaits the v4 batch's own async retry
        loop, so a native async transport configured on the context is used and
        independent batches truly overlap.
        """
        pending = self.pending_request()
        batch_request = ODataV4BatchRequest("", V4JsonFormat())
        batch_request.beforeExecute += pending.authenticate_request
        batch_request._async_authenticate = pending._async_authenticate
        if pending._auth_context.is_async_token_callback:
            # Batch payloads authenticate each sub-request synchronously during
            # ``build_request``; acquire (and cache) the token on the loop first so
            # that build can reuse it.
            await pending._auth_context.acquire_token_async()
        if pending.has_async_transport:
            batch_request.with_async_transport(pending.async_transport)
        await batch_request.execute_query_with_retry_async(batch_qry)
        return batch_qry.return_types

    def pending_request(self) -> GraphRequest:
        """Get or create the pending request"""
        if self._pending_request is None:
            self._pending_request = GraphRequest(
                tenant=self._tenant, environment=self._environment, authority=self._authority
            )
            if callable(self._token_callback):
                self._pending_request.with_access_token(self._token_callback)
        return self._pending_request  # type: ignore[return-value]

    @property
    def admin(self) -> Admin:
        """A container for administrator functionality for SharePoint and OneDrive."""
        return Admin(self, ResourcePath("admin"))

    @property
    def app_catalogs(self) -> AppCatalogs:
        """A container for apps from the Microsoft Teams app catalog."""
        return AppCatalogs(self, ResourcePath("appCatalogs"))

    @property
    def me(self) -> User:
        """The Me endpoint is provided as a shortcut for specifying the current user"""
        return User(self, MePath())

    @property
    def device_management(self) -> DeviceManagement:
        """Singleton entity that acts as a container for all device management functionality."""
        return DeviceManagement(self, ResourcePath("deviceManagement"))

    @property
    def device_app_management(self) -> DeviceAppManagement:
        """Singleton entity that acts as a container for all device and app management functionality."""
        return DeviceAppManagement(self, ResourcePath("deviceAppManagement"))

    @property
    def drives(self) -> "DriveCollection":
        """Get one drives"""
        return DriveCollection(self, ResourcePath("drives"))

    @property
    def users(self) -> UserCollection:
        """Users container"""
        return UserCollection(self, ResourcePath("users"))

    @property
    def domains(self) -> DomainCollection:
        """Get the tenant domains. Use ``ensure("contoso.com")`` for an idempotent add."""
        return DomainCollection(self, ResourcePath("domains"))

    @property
    def groups(self) -> GroupCollection:
        """Get groups"""
        return GroupCollection(self, ResourcePath("groups"))

    @property
    def invitations(self) -> InvitationCollection:
        """Get invitations"""
        return InvitationCollection(self, ResourcePath("invitations"))

    @property
    def copilot(self) -> CopilotRoot:
        """"""
        return CopilotRoot(self, ResourcePath("copilot"))

    @property
    def identity_protection(self) -> IdentityProtectionRoot:
        """Identity Protection alias"""
        return IdentityProtectionRoot(self, ResourcePath("identityProtection"))

    @property
    def sites(self) -> SitesWithRoot:
        """Sites container"""
        return SitesWithRoot(self, ResourcePath("sites"))

    @property
    def shares(self) -> SharesCollection:
        """Shares container"""
        return SharesCollection(self, ResourcePath("shares"))

    @property
    def directory_objects(self) -> DirectoryObjectCollection:
        """Directory Objects container"""
        return DirectoryObjectCollection(self, ResourcePath("directoryObjects"))

    @property
    def devices(self) -> DeviceCollection:
        """Devices container"""
        return DeviceCollection(self, ResourcePath("devices"))

    @property
    def teams(self) -> TeamCollection:
        """Teams container"""
        return TeamCollection(self, ResourcePath("teams"))

    @property
    def chats(self) -> ChatCollection:
        """Chats container"""
        return ChatCollection(self, ResourcePath("chats"))

    @property
    def group_setting_templates(self) -> EntityCollection[GroupSettingTemplate]:
        """Group setting templates represent system-defined settings available to the tenant."""
        return EntityCollection(self, GroupSettingTemplate, ResourcePath("groupSettingTemplates"))

    @property
    def contacts(self) -> DeltaCollection[OrgContact]:
        """Get the list of organizational contacts for this organization."""
        return DeltaCollection(self, OrgContact, ResourcePath("contacts"))

    @property
    def directory(self) -> Directory:
        """Represents a deleted item in the directory"""
        if self._directory is None:
            self._directory = Directory(self, ResourcePath("directory"))
        return self._directory

    @property
    def directory_roles(self) -> DirectoryRoleCollection:
        """Represents a directory roles in the directory"""
        return DirectoryRoleCollection(self, ResourcePath("directoryRoles"))

    @property
    def directory_role_templates(self) -> DirectoryRoleTemplateCollection:
        """Represents a directory role templates in the directory"""
        from office365.directory.rolemanagement.templates.collection import DirectoryRoleTemplateCollection

        return DirectoryRoleTemplateCollection(self, ResourcePath("directoryRoleTemplates"))

    @property
    def identity_providers(self) -> EntityCollection[IdentityProvider]:
        """"""
        return EntityCollection(self, IdentityProvider, ResourcePath("identityProviders"))

    @property
    def identity(self) -> IdentityContainer:
        return IdentityContainer(self, ResourcePath("identity"))

    @property
    def application_templates(self) -> EntityCollection[ApplicationTemplate]:
        """Get the list of application templates in this organization."""
        return EntityCollection(self, ApplicationTemplate, ResourcePath("applicationTemplates"))

    @property
    def authentication_method_configurations(
        self,
    ) -> EntityCollection[AuthenticationMethodConfiguration]:
        """Get the list of application templates in this organization."""
        return EntityCollection(
            self,
            AuthenticationMethodConfiguration,
            ResourcePath("authenticationMethodConfigurations"),
        )

    @property
    def applications(self) -> ApplicationCollection:
        """Get the list of applications in this organization."""
        return ApplicationCollection(self, ResourcePath("applications"))

    @property
    def certificate_based_auth_configuration(
        self,
    ) -> EntityCollection[CertificateBasedAuthConfiguration]:
        """Get the list of applications in this organization."""
        return EntityCollection(
            self,
            CertificateBasedAuthConfiguration,
            ResourcePath("certificateBasedAuthConfiguration"),
        )

    @property
    def service_principals(self) -> ServicePrincipalCollection:
        """Retrieve a list of servicePrincipal objects."""
        return ServicePrincipalCollection(self, ResourcePath("servicePrincipals"))

    @property
    def organization(self) -> EntityCollection[Organization]:
        """"""
        return EntityCollection(self, Organization, ResourcePath("organization"))

    @property
    def subscribed_skus(self) -> SubscribedSkuCollection:
        """Get the list of commercial subscriptions that an organization has acquired"""
        return SubscribedSkuCollection(self, ResourcePath("subscribedSkus"))

    @property
    def group_lifecycle_policies(self) -> EntityCollection[GroupLifecyclePolicy]:
        """A collection of lifecycle policies for a Microsoft 365 groups."""
        return EntityCollection(self, GroupLifecyclePolicy, ResourcePath("groupLifecyclePolicies"))

    @property
    def group_settings(self) -> GroupSetting:
        """Represents a directory roles in the directory"""
        from office365.directory.groups.setting import GroupSetting

        return GroupSetting(self, ResourcePath("groupSettings"))

    @property
    def communications(self) -> CloudCommunications:
        """Cloud communications API endpoint"""
        return CloudCommunications(self, ResourcePath("communications"))

    @property
    def identity_governance(self) -> IdentityGovernance:
        """The identity governance singleton"""
        return IdentityGovernance(self, ResourcePath("identityGovernance"))

    @property
    def information_protection(self) -> InformationProtection:
        """
        Exposes methods that you can use to get Microsoft Purview Information Protection labels and label policies.
        """
        return InformationProtection(self, ResourcePath("informationProtection"))

    @property
    def storage(self) -> Storage:
        """
        Facilitates the structures of fileStorageContainers.
        """
        return Storage(self, ResourcePath("storage"))

    @property
    def subscriptions(self) -> SubscriptionCollection:
        """
        Retrieve the properties and relationships of webhook subscriptions,
        based on the app ID, the user, and the user's role with a tenant.
        """
        return SubscriptionCollection(self, ResourcePath("subscriptions"))

    @property
    def connections(self) -> EntityCollection[ExternalConnection]:
        """Get a list of the externalConnection objects and their properties."""
        from office365.search.external.connection import ExternalConnection

        return EntityCollection(self, ExternalConnection, ResourcePath("connections"))

    @property
    def tenant_relationships(self) -> TenantRelationship:
        """Represent the various type of tenant relationships."""
        return TenantRelationship(self, ResourcePath("tenantRelationships"))

    @property
    def audit_logs(self) -> AuditLogRoot:
        """Gets the list of audit logs generated by Azure Active Directory."""
        return AuditLogRoot(self, ResourcePath("auditLogs"))

    @property
    def places(self) -> PlaceCollection:
        """Gets all places in a tenant"""
        return PlaceCollection(self, ResourcePath("places"))

    @property
    def oauth2_permission_grants(self) -> OAuth2PermissionGrantCollection:
        """Permission grants container"""
        return OAuth2PermissionGrantCollection(self, ResourcePath("oauth2PermissionGrants"))

    @property
    def room_lists(self) -> EntityCollection[RoomList]:
        """Gets all the room lists in a tenant"""
        return EntityCollection(
            self,
            RoomList,
            ResourcePath("microsoft.graph.roomlist", ResourcePath("places")),
        )

    @property
    def reports(self) -> ReportRoot:
        """Represents a container for Azure Active Directory (Azure AD) reporting resources."""
        return ReportRoot(self, ResourcePath("reports"))

    @property
    def role_management(self) -> RoleManagement:
        """Represents a Microsoft 365 role-based access control (RBAC) role management container"""
        return RoleManagement(self, ResourcePath("roleManagement"))

    @property
    def solutions(self) -> SolutionsRoot:
        return SolutionsRoot(self, ResourcePath("solutions"))

    @property
    def teams_templates(self) -> EntityCollection[TeamsTemplate]:
        """Get the list of teams templates."""
        return EntityCollection(self, TeamsTemplate, ResourcePath("teamsTemplates"))

    @property
    def planner(self) -> Planner:
        """
        The planner resource is the entry point for the Planner object model.
        It returns a singleton planner resource. It doesn't contain any usable properties.
        """
        return Planner(self, ResourcePath("planner"))

    @property
    def permission_grants(self) -> EntityCollection[ResourceSpecificPermissionGrant]:
        """List all resource-specific permission grants"""
        return EntityCollection(self, ResourceSpecificPermissionGrant, ResourcePath("permissionGrants"))

    @property
    def print(self) -> Print:
        """Used to manage printers and print jobs within Universal Print."""
        return Print(self, ResourcePath("print"))

    @property
    def search(self) -> SearchEntity:
        """The search endpoint is the entry point for Microsoft Search API to query data."""
        return SearchEntity(self, ResourcePath("search"))

    @property
    def employee_experience(self) -> EmployeeExperience:
        """An alias to EmployeeExperience"""
        return EmployeeExperience(self, ResourcePath("employeeExperience"))

    @property
    def education(self) -> EducationRoot:
        """
        The /education namespace exposes functionality that is specific to the education sector.
        """
        return EducationRoot(self, ResourcePath("education"))

    @property
    def policies(self) -> PolicyRoot:
        """Resource type exposing navigation properties for the policies singleton."""
        return PolicyRoot(self, ResourcePath("policies"))

    @property
    def external(self) -> External:
        """A logical container for external sources."""
        return External(self, ResourcePath("external"))

    @property
    def security(self) -> Security:
        """The security resource is the entry point for the Security object model.
        It returns a singleton security resource. It doesn't contain any usable properties.
        """
        return Security(self, ResourcePath("security"))

    @property
    def schema_extensions(self) -> EntityCollection[SchemaExtension]:
        """Get a list of schemaExtension objects in your tenant"""
        return EntityCollection(self, SchemaExtension, ResourcePath("schemaExtensions"))

    @property
    def teamwork(self) -> Teamwork:
        """A container for the range of Microsoft Teams functionalities that are available for the organization."""
        return Teamwork(self, ResourcePath("teamwork"))

    @property
    def tenant_name(self) -> Optional[str]:
        """Tenant id or domain name"""
        return self._tenant

    def has_delegated_permission(self, scope: str, app_id: str) -> bool:
        """Check if an app has a delegated permission on Microsoft Graph.

        Args:
            scope (str): Permission scope name (e.g. 'Mail.Read')
            app_id (str): Application (client) ID of the app to check
        """
        from office365.directory.permissions.guard import has_delegated_permission as _check

        return _check(self, scope, app_id)

    def has_application_permissions(self, scope: str, app_id: str) -> bool:
        """Check if an app has an application permission on Microsoft Graph.

        Args:
            scope (str): Permission scope name (e.g. 'Mail.Read')
            app_id (str): Application (client) ID of the app to check
        """
        granted = self.get_application_permissions(app_id).execute_query().value
        return any(role.value == scope for role in granted)

    def grant_delegated_permissions(self, app_id: str, scope: AppRole | str) -> Self:
        """Grants a delegated permission on Microsoft Graph (AllPrincipals).

        Args:
            app_id (str): Application (client) ID of the client app
            scope (AppRole or str): Permission scope to grant
        """
        from office365.directory.permissions.resource_name import ResourceName

        self.service_principals.find_by_name(ResourceName.Graph, required=True).grant_delegated_permissions(
            app_id, scope
        )
        return self

    def get_delegated_permissions(self, app_id: str) -> ClientResult[StringCollection]:
        """Gets delegated permissions granted on Microsoft Graph.

        Args:
            app_id (str): Application (client) ID of the client app
        """
        from office365.directory.permissions.resource_name import ResourceName

        return self.service_principals.find_by_name(ResourceName.Graph, required=True).get_delegated_permissions(app_id)

    def grant_application_permissions(self, app_id: str, app_role: AppRole | str) -> Self:
        """Grants an application permission on Microsoft Graph.

        Args:
            app_id (str): Application (client) ID of the client app
            app_role (AppRole or str): App role to grant
        """
        from office365.directory.permissions.resource_name import ResourceName

        self.service_principals.find_by_name(ResourceName.Graph, required=True).grant_application_permissions(
            app_id, app_role
        )
        return self

    def get_application_permissions(self, app_id: str) -> ClientResult[AppRoleCollection]:
        """Gets application permissions granted on Microsoft Graph.

        Args:
            app_id (str): Application (client) ID of the client app
        """
        from office365.directory.permissions.resource_name import ResourceName

        return self.service_principals.find_by_name(ResourceName.Graph, required=True).get_application_permissions(
            app_id
        )

    def revoke_delegated_permissions(self, client_id: str, scope: str) -> Self:
        """Revokes a delegated permission on Microsoft Graph.

        Args:
            client_id (str): Application (client) ID of the client app
            scope (str): Permission scope to revoke
        """
        from office365.directory.permissions.resource_name import ResourceName

        self.service_principals.find_by_name(ResourceName.Graph, required=True).revoke_delegated_permissions(
            client_id, scope
        )
        return self

    def revoke_application_permissions(self, app_id: str, app_role: AppRole | str) -> Self:
        """Revokes an application permission on Microsoft Graph.

        Args:
            app_id (str): Application (client) ID of the client app
            app_role (AppRole or str): App role to revoke
        """
        from office365.directory.permissions.resource_name import ResourceName

        self.service_principals.find_by_name(ResourceName.Graph, required=True).revoke_application_permissions(
            app_id, app_role
        )
        return self
