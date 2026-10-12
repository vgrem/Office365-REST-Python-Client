from __future__ import annotations

import base64
import os
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from typing_extensions import Self

from office365.directory.applications.api import ApiApplication
from office365.directory.applications.nativeauthenticationapisenabled import (
    NativeAuthenticationApisEnabled,
)
from office365.directory.applications.optional_claims import OptionalClaims
from office365.directory.applications.parentalcontrolsettings import (
    ParentalControlSettings,
)
from office365.directory.applications.public_client import PublicClientApplication
from office365.directory.applications.requestsignatureverification import (
    RequestSignatureVerification,
)
from office365.directory.applications.required_resource_access import (
    RequiredResourceAccess,
)
from office365.directory.applications.roles.role import AppRole
from office365.directory.applications.spa import SpaApplication
from office365.directory.applications.verifiedpublisher import VerifiedPublisher
from office365.directory.applications.web import WebApplication
from office365.directory.authentication.behaviors import AuthenticationBehaviors
from office365.directory.certificates.certification import Certification
from office365.directory.extensions.extension_property import ExtensionProperty
from office365.directory.key_credential import KeyCredential
from office365.directory.objects.addin import AddIn
from office365.directory.objects.collection import DirectoryObjectCollection
from office365.directory.objects.informationalurl import InformationalUrl
from office365.directory.objects.object import DirectoryObject
from office365.directory.password_credential import PasswordCredential
from office365.directory.permissions.require_permission import require_permission
from office365.directory.permissions.resource_name import ResourceName
from office365.directory.policies.token_issuance import TokenIssuancePolicy
from office365.directory.serviceprincipals.lockconfiguration import (
    ServicePrincipalLockConfiguration,
)
from office365.directory.synchronization.synchronization import Synchronization
from office365.entity_collection import EntityCollection
from office365.runtime.auth.certificate import certificate_der as _certificate_der
from office365.runtime.auth.certificate import (
    certificate_thumbprint as _certificate_thumbprint,
)
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.v4.entity import EntityPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import GuidCollection, StringCollection
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.directory.policies.app_management import AppManagementPolicy
    from office365.directory.policies.home_realm_discovery import (
        HomeRealmDiscoveryPolicy,
    )
    from office365.directory.policies.token_lifetime import TokenLifetimePolicy
    from office365.directory.serviceprincipals.federated_identity_credential import (
        FederatedIdentityCredential,
    )
    from office365.directory.serviceprincipals.service_principal import ServicePrincipal


class Application(DirectoryObject):
    """
    Represents an application. Any application that outsources authentication to Azure Active Directory (Azure AD)
    must be registered in a directory. Application registration involves telling Azure AD about your application,
    including the URL where it's located, the URL to send replies after authentication,
    the URI to identify your application, and more. For more information, see Basics of Registering
    an Application in Azure AD
    """

    def __repr__(self):
        return self.id or self.app_id or self.entity_type_name

    def __str__(self):
        return self.display_name or self.app_id or self.entity_type_name

    @staticmethod
    def certificate_thumbprint(cert_data: bytes | bytearray | str | os.PathLike[str]) -> str:
        """Compute the SHA-1 thumbprint of a certificate.

        Returns the upper-case hex string that Entra stores in
        ``keyCredential.customKeyIdentifier`` and that MSAL expects for
        certificate authentication. The certificate may be supplied as raw
        DER/PEM bytes, inline PEM text, or a file path.

        Args:
            cert_data: The certificate's raw DER/PEM bytes, inline PEM text, or a file path.
        """
        return _certificate_thumbprint(cert_data)

    @require_permission(delegated=["Application.ReadWrite.All"], application=["Application.ReadWrite.All"])
    def add_certificate(
        self,
        cert_data: bytes | bytearray | str | os.PathLike[str],
        display_name: str,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> Self:
        """Adds a certificate to an application.

        Args:
            cert_data: The certificate's raw DER/PEM bytes, inline PEM text, or a file path.
            display_name (str): Friendly name for the key.
            start_datetime (datetime.datetime): The date and time at which the credential becomes valid. Default: now
            end_datetime (datetime.datetime): The date and time at which the credential expires. Default: now + 180days
        """
        if start_datetime is None:
            start_datetime = datetime.now(timezone.utc)
        if end_datetime is None:
            end_datetime = start_datetime + timedelta(days=180)
        params = KeyCredential(
            usage="Verify",
            type="AsymmetricX509Cert",
            startDateTime=start_datetime,
            endDateTime=end_datetime,
            key=base64.b64encode(_certificate_der(cert_data)).decode("utf-8"),
            displayName=f"CN={display_name}",
        )
        self.key_credentials.add(params)
        self.update()
        return self

    @require_permission(delegated=["Application.ReadWrite.All"], application=["Application.ReadWrite.All"])
    def ensure_certificate(
        self,
        cert_data: bytes | bytearray | str | os.PathLike[str],
        display_name: str,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> Self:
        """Attaches a certificate to an application unless it is already attached.

        The certificate may be supplied as raw DER/PEM bytes, inline PEM text, or a
        file path. Its SHA-1 thumbprint is compared against the application's
        existing ``keyCredentials`` so that repeating a setup run does not add
        duplicate credentials. Requires ``Application.ReadWrite.All``.

        Args:
            cert_data: The certificate's raw DER/PEM bytes, inline PEM text, or a file path.
            display_name (str): Friendly name for the key.
            start_datetime (datetime.datetime): The date and time at which the credential becomes valid. Default: now
            end_datetime (datetime.datetime): The date and time at which the credential expires. Default: now + 180days
        """
        thumbprint = _certificate_thumbprint(cert_data)

        def _attach(_: Any) -> None:
            attached = {c.customKeyIdentifier.upper() for c in self.key_credentials if c.customKeyIdentifier}
            if thumbprint not in attached:
                self.add_certificate(cert_data, display_name, start_datetime, end_datetime)

        self.ensure_property("keyCredentials").after_execute(_attach)
        return self

    def remove_certificate(self, thumbprint: str) -> Self:
        """Remove a certificate from an application.

        Args:
            thumbprint (str): The unique identifier for the password.
        """
        raise NotImplementedError("remove_certificate")

    @require_permission(
        delegated=["AppRoleAssignment.ReadWrite.All"],
        application=["AppRoleAssignment.ReadWrite.All"],
    )
    def grant_permissions(
        self,
        scope: str,
        resource: str | ResourceName = ResourceName.Graph,
    ) -> Self:
        """Grant this application an application permission (app role) on a resource.

        Idempotent — re-running once the permission is granted is a no-op. The
        app role assignment is created on the resource's service principal, so
        ``AppRoleAssignment.ReadWrite.All`` (with admin consent) is required.
        Deferred; resolve with ``execute_query()``:

            app = client.applications.ensure("my-app").execute_query()
            app.grant_permissions("Sites.Selected", MsAppIds.Office_365_SharePoint_Online).execute_query()

        Args:
            scope: The app role (permission) name, e.g. ``"Sites.Selected"``.
            resource: The resource application that exposes the role, identified
                by application (client) ID (e.g. ``MsAppIds.Office_365_SharePoint_Online``)
                or display name (e.g. ``ResourceName.SharePoint``).
        """
        resource_sp = self._resolve_resource_sp(resource)

        def _grant(_: Any) -> None:
            assert self.app_id is not None
            resource_sp.grant_application_permissions(self.app_id, scope)

        self.ensure_property("appId").after_execute(_grant)
        return self

    @require_permission(
        delegated=["AppRoleAssignment.ReadWrite.All"],
        application=["AppRoleAssignment.ReadWrite.All"],
    )
    def revoke_permissions(
        self,
        scope: str,
        resource: str | ResourceName = ResourceName.Graph,
    ) -> Self:
        """Revoke a previously granted application permission (app role) from this application.

        A no-op when the permission is not assigned, so it is safe to re-run. The
        app role assignment lives on the resource's service principal, so
        ``AppRoleAssignment.ReadWrite.All`` (with admin consent) is required.
        Deferred; resolve with ``execute_query()``:

            app.revoke_permissions("Sites.Selected", MsAppIds.Office_365_SharePoint_Online).execute_query()

        Args:
            scope: The app role (permission) name, e.g. ``"Sites.Selected"``.
            resource: The resource application that exposes the role, identified
                by application (client) ID (e.g. ``MsAppIds.Office_365_SharePoint_Online``)
                or display name (e.g. ``ResourceName.SharePoint``).
        """
        resource_sp = self._resolve_resource_sp(resource)

        def _revoke(_: Any) -> None:
            assert self.app_id is not None
            resource_sp.revoke_application_permissions(self.app_id, scope)

        self.ensure_property("appId").after_execute(_revoke)
        return self

    def _resolve_resource_sp(self, resource: str | ResourceName) -> ServicePrincipal:
        """Resolve a resource app's service principal from a client ID or display name."""
        value = str(resource)
        try:
            UUID(value)
        except (TypeError, ValueError):
            return self.context.service_principals.find_by_name(value, required=True)
        return self.context.service_principals.get_by_app_id(value)

    @require_permission(delegated=["Application.ReadWrite.All"], application=["Application.ReadWrite.All"])
    def add_password(self, display_name: str) -> ClientResult[PasswordCredential]:
        """Adds a strong password to an application.

        Args:
            display_name (str): App display name
        """
        params = PasswordCredential(displayName=display_name)
        result = ClientResult(self.context, params)
        qry = ServiceOperationQuery(self, "addPassword", None, params, None, result)
        self.context.add_query(qry)
        return result

    @require_permission(delegated=["Application.ReadWrite.All"], application=["Application.ReadWrite.All"])
    def remove_password(self, key_id: str) -> Self:
        """Remove a password from an application.

        Args:
            key_id (str): The unique identifier for the password.
        """
        qry = ServiceOperationQuery(self, "removePassword", None, {"keyId": key_id})
        self.context.add_query(qry)
        return self

    @require_permission(delegated=["Application.ReadWrite.All"], application=["Application.ReadWrite.All"])
    def delete_object(self, permanent_delete: bool = False, *, ignore_missing: bool = False) -> Self:
        """Args:
        permanent_delete (bool): Permanently deletes the application from directory
        ignore_missing (bool): Treat deleting a missing application as success
        """
        super().delete_object(ignore_missing=ignore_missing)
        deleted_app = DirectoryObject(
            self.context, EntityPath(self.id, self.context.directory.deleted_applications.resource_path)
        )
        self.context.directory.deleted_applications.add_child(deleted_app)
        if permanent_delete:
            deleted_app.delete_object(ignore_missing=ignore_missing)
        return self

    @require_permission(delegated=["Application.ReadWrite.All"], application=["Application.ReadWrite.All"])
    def set_verified_publisher(self, verified_publisher_id: str) -> Self:
        """Set the verifiedPublisher on an application.
        For more information, including prerequisites to setting a verified publisher, see Publisher verification.

        Args:
            verified_publisher_id (str): The Microsoft Partner Network ID (MPNID) of the verified publisher to be set
              on the application, from the publisher's Partner Center account.
        """
        qry = ServiceOperationQuery(self, "setVerifiedPublisher", None, {"verifiedPublisherId": verified_publisher_id})
        self.context.add_query(qry)
        return self

    @require_permission(delegated=["Application.ReadWrite.All"], application=["Application.ReadWrite.All"])
    def unset_verified_publisher(self) -> Self:
        """Unset the verifiedPublisher previously set on an application, removing all verified publisher properties.
        For more information, see Publisher verification.
        """
        qry = ServiceOperationQuery(self, "unsetVerifiedPublisher")
        self.context.add_query(qry)
        return self

    @require_permission(delegated=["Application.ReadWrite.All"], application=["Application.ReadWrite.All"])
    def add_key(
        self, key_credential: KeyCredential, password_credential: PasswordCredential, proof: str
    ) -> ClientResult[KeyCredential]:
        """Add a key credential to an application. This method, along with removeKey can be used by an application
        to automate rolling its expiring keys.

        Args:
            key_credential (KeyCredential): The new application key credential to add. The type, usage and key
               are required properties for this usage. Supported key types are: AsymmetricX509Cert:
               The usage must be Verify. X509CertAndPassword: The usage must be Sign
            password_credential (PasswordCredential): Only secretText is required to be set which should contain
              the password for the key. This property is required only for keys of type X509CertAndPassword.
              Set it to null otherwise.
            proof (str): A self-signed JWT token used as a proof of possession of the existing keys
        """
        payload = {"keyCredential": key_credential, "passwordCredential": password_credential, "proof": proof}
        return_type = ClientResult(self.context, KeyCredential())
        qry = ServiceOperationQuery(self, "addKey", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(delegated=["Application.ReadWrite.All"], application=["Application.ReadWrite.All"])
    def remove_key(self, key_id: str, proof: str) -> Self:
        """Remove a key credential from an application.
        This method along with addKey can be used by an application to automate rolling its expiring keys.

        Args:
            key_id (str): The unique identifier for the password.
            proof (str): A self-signed JWT token used as a proof of possession of the existing keys. This JWT token
              must be signed using the private key of one of the application's existing valid certificates.
              The token should contain the following claims: aud -
              Audience needs to be 00000002-0000-0000-c000-000000000000. iss - Issuer needs to be the id of
                the application that is making the call. nbf - Not before time. exp - Expiration time should be
                "nbf" + 10 mins.
        """
        qry = ServiceOperationQuery(self, "removeKey", None, {"keyId": key_id, "proof": proof})
        self.context.add_query(qry)
        return self

    @property
    def app_id(self) -> Optional[str]:
        """The unique identifier for the application that is assigned to an application by Azure AD. Not nullable."""
        return self.properties.get("appId", None)

    @property
    def application_template_id(self) -> Optional[str]:
        """Unique identifier of the applicationTemplate"""
        return self.properties.get("applicationTemplateId", None)

    @odata(name="appRoles")
    @property
    def app_roles(self) -> ClientValueCollection[AppRole]:
        """
        The collection of roles defined for the application. With app role assignments, these roles can be assigned to
        users, groups, or service principals associated with other applications
        """
        return self.properties.get("appRoles", ClientValueCollection(AppRole))

    @property
    def api(self) -> ApiApplication:
        """Specifies settings for an application that implements a web API."""
        return self.properties.get("api", ApiApplication())

    @property
    def certification(self) -> Certification:
        """Specifies the certification status of the application."""
        return self.properties.get("certification", Certification())

    @odata(name="createdDateTime")
    @property
    def created_datetime(self):
        """The date and time the application was registered."""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def default_redirect_uri(self) -> Optional[str]:
        """ """
        return self.properties.get("defaultRedirectUri", None)

    @property
    def spa(self) -> SpaApplication:
        """
        Specifies settings for a single-page application, including sign out URLs and redirect URIs for
        authorization codes and access tokens."""
        return self.properties.get("spa", SpaApplication())

    @odata(name="keyCredentials", persist=True)
    @property
    def key_credentials(self) -> ClientValueCollection[KeyCredential]:
        """The collection of key credentials associated with the application. Not nullable."""
        return self.properties.setdefault("keyCredentials", ClientValueCollection(KeyCredential))

    @property
    def display_name(self) -> Optional[str]:
        """
        The display name for the application.
        Supports $filter (eq, ne, NOT, ge, le, in, startsWith), $search, and $orderBy.
        """
        return self.properties.get("displayName", None)

    @property
    def identifier_uris(self) -> StringCollection:
        """
        The URIs that identify the application within its Azure AD tenant, or within a verified custom domain
        if the application is multi-tenant. For more information see Application Objects and Service Principal Objects.
        The any operator is required for filter expressions on multi-valued properties.
        """
        return self.properties.get("identifierUris", StringCollection())

    @odata(name="optionalClaims")
    @property
    def optional_claims(self) -> OptionalClaims:
        """Application developers can configure optional claims in their Microsoft Entra applications to specify
        the claims that are sent to their application by the Microsoft security token service.
        """
        return self.properties.get("optionalClaims", OptionalClaims())

    @odata(name="passwordCredentials")
    @property
    def password_credentials(self) -> ClientValueCollection[PasswordCredential]:
        """The collection of password credentials associated with the application"""
        return self.properties.get("passwordCredentials", ClientValueCollection(PasswordCredential))

    @odata(name="publicClient")
    @property
    def public_client(self) -> PublicClientApplication:
        """Specifies settings for installed clients such as desktop or mobile devices."""
        return self.properties.get("publicClient", PublicClientApplication())

    @property
    def signin_audience(self) -> Optional[str]:
        """
        Specifies the Microsoft accounts that are supported for the current application.
        Supported values are: AzureADMyOrg, AzureADMultipleOrgs, AzureADandPersonalMicrosoftAccount,
        PersonalMicrosoftAccount
        """
        return self.properties.get("signInAudience", None)

    @odata(name="createdOnBehalfOf")
    @property
    def created_on_behalf_of(self) -> DirectoryObject:
        """"""
        return self.properties.get(
            "createdOnBehalfOf", DirectoryObject(self.context, ResourcePath("createdOnBehalfOf", self.resource_path))
        )

    @property
    def owners(self) -> DirectoryObjectCollection:
        """Directory objects that are owners of the application."""
        return self.properties.get(
            "owners", DirectoryObjectCollection(self.context, ResourcePath("owners", self.resource_path))
        )

    @odata(name="extensionProperties")
    @property
    def extension_properties(self) -> EntityCollection[ExtensionProperty]:
        """List extension properties on an application object."""
        return self.properties.get(
            "extensionProperties",
            EntityCollection(self.context, ExtensionProperty, ResourcePath("extensionProperties", self.resource_path)),
        )

    @odata(name="requiredResourceAccess")
    @property
    def required_resource_access(self) -> ClientValueCollection[RequiredResourceAccess]:
        """Specifies the resources that the application needs to access. This property also specifies the set
        of delegated permissions and application roles that it needs for each of those resources.
        This configuration of access to the required resources drives the consent experience.
        """
        return self.properties.get("requiredResourceAccess", ClientValueCollection(RequiredResourceAccess))

    @odata(name="tokenIssuancePolicies")
    @property
    def token_issuance_policies(self) -> EntityCollection[TokenIssuancePolicy]:
        """Get all tokenIssuancePolicies assigned to this object."""
        return self.properties.get(
            "tokenIssuancePolicies",
            EntityCollection(
                self.context, TokenIssuancePolicy, ResourcePath("tokenIssuancePolicies", self.resource_path)
            ),
        )

    @odata(name="addIns")
    @property
    def add_ins(self) -> ClientValueCollection[AddIn]:
        """Gets the addIns property"""
        return self.properties.get("addIns", ClientValueCollection[AddIn](AddIn))

    @odata(name="authenticationBehaviors")
    @property
    def authentication_behaviors(self) -> AuthenticationBehaviors:
        """Gets the authenticationBehaviors property"""
        return self.properties.get("authenticationBehaviors", AuthenticationBehaviors())

    @property
    def created_by_app_id(self) -> Optional[str]:
        """Gets the createdByAppId property"""
        return self.properties.get("createdByAppId", None)

    @odata(name="createdDateTime")
    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def disabled_by_microsoft_status(self) -> Optional[str]:
        """Gets the disabledByMicrosoftStatus property"""
        return self.properties.get("disabledByMicrosoftStatus", None)

    @property
    def group_membership_claims(self) -> Optional[str]:
        """Gets the groupMembershipClaims property"""
        return self.properties.get("groupMembershipClaims", None)

    @property
    def info(self) -> InformationalUrl:
        """Gets the info property"""
        return self.properties.get("info", InformationalUrl())

    @property
    def is_device_only_auth_supported(self) -> Optional[bool]:
        """Gets the isDeviceOnlyAuthSupported property"""
        return self.properties.get("isDeviceOnlyAuthSupported", None)

    @property
    def is_disabled(self) -> Optional[bool]:
        """Gets the isDisabled property"""
        return self.properties.get("isDisabled", None)

    @property
    def is_fallback_public_client(self) -> Optional[bool]:
        """Gets the isFallbackPublicClient property"""
        return self.properties.get("isFallbackPublicClient", None)

    @property
    def logo(self) -> bytes | None:
        """Gets the logo property"""
        return self.properties.get("logo", None)

    @property
    def manager_applications(self) -> GuidCollection:
        """Gets the managerApplications property"""
        return self.properties.get("managerApplications", GuidCollection(None))

    @property
    def native_authentication_apis_enabled(self) -> NativeAuthenticationApisEnabled:
        """Gets the nativeAuthenticationApisEnabled property"""
        return self.properties.get("nativeAuthenticationApisEnabled", NativeAuthenticationApisEnabled.none)

    @property
    def notes(self) -> Optional[str]:
        """Gets the notes property"""
        return self.properties.get("notes", None)

    @property
    def oauth2_require_post_response(self) -> Optional[bool]:
        """Gets the oauth2RequirePostResponse property"""
        return self.properties.get("oauth2RequirePostResponse", None)

    @property
    def parental_control_settings(self) -> ParentalControlSettings:
        """Gets the parentalControlSettings property"""
        return self.properties.get("parentalControlSettings", ParentalControlSettings())

    @property
    def publisher_domain(self) -> Optional[str]:
        """Gets the publisherDomain property"""
        return self.properties.get("publisherDomain", None)

    @property
    def request_signature_verification(self) -> RequestSignatureVerification:
        """Gets the requestSignatureVerification property"""
        return self.properties.get("requestSignatureVerification", RequestSignatureVerification())

    @property
    def saml_metadata_url(self) -> Optional[str]:
        """Gets the samlMetadataUrl property"""
        return self.properties.get("samlMetadataUrl", None)

    @property
    def service_management_reference(self) -> Optional[str]:
        """Gets the serviceManagementReference property"""
        return self.properties.get("serviceManagementReference", None)

    @property
    def service_principal_lock_configuration(self) -> ServicePrincipalLockConfiguration:
        """Gets the servicePrincipalLockConfiguration property"""
        return self.properties.get("servicePrincipalLockConfiguration", ServicePrincipalLockConfiguration())

    @property
    def sign_in_audience(self) -> Optional[str]:
        """Gets the signInAudience property"""
        return self.properties.get("signInAudience", None)

    @property
    def tags(self) -> StringCollection:
        """Gets the tags property"""
        return self.properties.get("tags", StringCollection(None))

    @property
    def token_encryption_key_id(self) -> Optional[UUID]:
        """Gets the tokenEncryptionKeyId property"""
        return self.properties.get("tokenEncryptionKeyId", None)

    @property
    def unique_name(self) -> Optional[str]:
        """Gets the uniqueName property"""
        return self.properties.get("uniqueName", None)

    @property
    def verified_publisher(self) -> VerifiedPublisher:
        """Gets the verifiedPublisher property"""
        return self.properties.get("verifiedPublisher", VerifiedPublisher())

    @property
    def web(self) -> WebApplication:
        """Gets the web property"""
        return self.properties.get("web", WebApplication())

    @property
    def synchronization(self) -> Synchronization:
        """Gets the synchronization property"""
        return self.properties.get(
            "synchronization", Synchronization(self.context, ResourcePath("synchronization", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Application"

    @property
    def app_management_policies(self) -> EntityCollection[AppManagementPolicy]:
        """Gets the appManagementPolicies property"""
        from office365.directory.policies.app_management import AppManagementPolicy

        return self.properties.get(
            "appManagementPolicies",
            EntityCollection[AppManagementPolicy](
                self.context, AppManagementPolicy, ResourcePath("appManagementPolicies", self.resource_path)
            ),
        )

    @property
    def federated_identity_credentials(self) -> EntityCollection[FederatedIdentityCredential]:
        """Gets the federatedIdentityCredentials property"""
        from office365.directory.serviceprincipals.federated_identity_credential import (
            FederatedIdentityCredential,
        )

        return self.properties.get(
            "federatedIdentityCredentials",
            EntityCollection[FederatedIdentityCredential](
                self.context,
                FederatedIdentityCredential,
                ResourcePath("federatedIdentityCredentials", self.resource_path),
            ),
        )

    @property
    def home_realm_discovery_policies(self) -> EntityCollection[HomeRealmDiscoveryPolicy]:
        """Gets the homeRealmDiscoveryPolicies property"""
        from office365.directory.policies.home_realm_discovery import (
            HomeRealmDiscoveryPolicy,
        )

        return self.properties.get(
            "homeRealmDiscoveryPolicies",
            EntityCollection[HomeRealmDiscoveryPolicy](
                self.context, HomeRealmDiscoveryPolicy, ResourcePath("homeRealmDiscoveryPolicies", self.resource_path)
            ),
        )

    @property
    def token_lifetime_policies(self) -> EntityCollection[TokenLifetimePolicy]:
        """Gets the tokenLifetimePolicies property"""
        from office365.directory.policies.token_lifetime import TokenLifetimePolicy

        return self.properties.get(
            "tokenLifetimePolicies",
            EntityCollection[TokenLifetimePolicy](
                self.context, TokenLifetimePolicy, ResourcePath("tokenLifetimePolicies", self.resource_path)
            ),
        )
