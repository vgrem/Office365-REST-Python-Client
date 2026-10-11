from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from typing_extensions import Self

from office365.delta_collection import DeltaCollection
from office365.directory.applications.roles.assignment_collection import (
    AppRoleAssignmentCollection,
)
from office365.directory.applications.roles.collection import AppRoleCollection
from office365.directory.applications.roles.role import AppRole
from office365.directory.certificates.self_signed import SelfSignedCertificate
from office365.directory.key_credential import KeyCredential
from office365.directory.objects.collection import DirectoryObjectCollection
from office365.directory.objects.object import DirectoryObject
from office365.directory.password_credential import PasswordCredential
from office365.directory.permissions.grants.oauth2 import OAuth2PermissionGrant
from office365.directory.permissions.grants.oauth2_collection import (
    OAuth2PermissionGrantCollection,
)
from office365.directory.permissions.scope import PermissionScope
from office365.directory.synchronization.synchronization import Synchronization
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.appid import AppIdPath
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.common.endpoint import Endpoint
    from office365.directory.applications.verifiedpublisher import VerifiedPublisher
    from office365.directory.objects.addin import AddIn
    from office365.directory.objects.customsecurityattributevalue import (
        CustomSecurityAttributeValue,
    )
    from office365.directory.objects.informationalurl import InformationalUrl
    from office365.directory.permissions.grants.resourcespecificpermission import (
        ResourceSpecificPermission,
    )
    from office365.directory.policies.app_management import AppManagementPolicy
    from office365.directory.policies.claims_mapping_policy import ClaimsMappingPolicy
    from office365.directory.policies.home_realm_discovery import (
        HomeRealmDiscoveryPolicy,
    )
    from office365.directory.policies.token_issuance import TokenIssuancePolicy
    from office365.directory.policies.token_lifetime import TokenLifetimePolicy
    from office365.directory.serviceprincipals.delegated_permission_classification import (
        DelegatedPermissionClassification,
    )
    from office365.directory.serviceprincipals.federated_identity_credential import (
        FederatedIdentityCredential,
    )
    from office365.directory.serviceprincipals.remote_desktop_security_configuration import (
        RemoteDesktopSecurityConfiguration,
    )
    from office365.directory.serviceprincipals.samlsinglesignonsettings import (
        SamlSingleSignOnSettings,
    )


class ServicePrincipal(DirectoryObject):
    """Represents an instance of an application in a directory."""

    def __str__(self):
        return self.display_name or ""

    def add_key(
        self,
        key_credential: KeyCredential,
        password_credential: PasswordCredential,
        proof: str,
    ) -> ClientResult[KeyCredential]:
        """Adds a key credential to a servicePrincipal. This method along with removeKey can be used by a
        servicePrincipal to automate rolling its expiring keys.

        Args:
            key_credential (KeyCredential): The new application key credential to add. The type, usage and key are
              required properties for this usage. Supported key types are: AsymmetricX509Cert:
              The usage must be Verify. X509CertAndPassword: The usage must be Sign
            password_credential (PasswordCredential): Only secretText is required to be set which should contain
              the password for the key. This property is required only for keys of type X509CertAndPassword.
              Set it to null otherwise.
            proof (str): A self-signed JWT token used as a proof of possession of the existing keys
        """
        payload = {
            "keyCredential": key_credential,
            "passwordCredential": password_credential,
            "proof": proof,
        }
        return_type = ClientResult(self.context, KeyCredential())
        qry = ServiceOperationQuery(self, "addKey", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_password(self, display_name: str | None = None) -> ClientResult[PasswordCredential]:
        """Adds a strong password to an application.

        Args:
            display_name (str): App display name
        """
        params = PasswordCredential(displayName=display_name)
        return_type = ClientResult(self.context, params)
        qry = ServiceOperationQuery(self, "addPassword", None, params, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_token_signing_certificate(
        self, display_name: str, end_datetime: str | None = None
    ) -> ClientResult[SelfSignedCertificate]:
        """Create a self-signed signing certificate and return a selfSignedCertificate object, which is the public part
        of the generated certificate.

        The self-signed signing certificate is composed of the following objects,
        which are added to the servicePrincipal:

        The keyCredentials object with the following objects:
        A private key object with usage set to Sign.
        A public key object with usage set to Verify.
        The passwordCredentials object.
        All the objects have the same value of customKeyIdentifier.

        The passwordCredential is used to open the PFX file (private key). It and the associated private key object
        have the same value of keyId. When set during creation through the displayName property, the subject of the
        certificate cannot be updated. The startDateTime is set to the same time the certificate is created using
        the action. The endDateTime can be up to three years after the certificate is created.

        Args:
            display_name (str): Friendly name for the key. It must start with CN=.
            end_datetime (str): The date and time when the credential expires. It can be up to 3 years from the
              date the certificate is created. If not supplied, the default is three years from the time of creation.
              The timestamp type represents date and time information using ISO 8601 format and is always in UTC time.
              For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
        """
        payload = {"displayName": display_name, "endDateTime": end_datetime}
        return_type = ClientResult(self.context, SelfSignedCertificate())
        qry = ServiceOperationQuery(self, "addTokenSigningCertificate", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_delegated_permissions(self, app_id: str) -> ClientResult[StringCollection]:
        """Gets delegated API permissions for the client app (AllPrincipals grants only)."""
        return_type = ClientResult(self.context, StringCollection())

        def _on_grants_loaded(col: OAuth2PermissionGrantCollection):
            found = next((g for g in col if g.resource_id == self.id), None)
            if found is not None and found.scope is not None:
                for name in found.scope.split(" "):
                    return_type.value.add(name)

        def _resolve_application():
            def _get_grant(sp: ServicePrincipal):
                self.context.oauth2_permission_grants.get().filter(
                    f"clientId eq '{sp.id}' and consentType eq 'AllPrincipals'"
                ).after_execute(_on_grants_loaded)

            self.context.service_principals.get_by_app_id(app_id).get().after_execute(_get_grant)

        self.ensure_property("id").after_execute(lambda _: _resolve_application())
        return return_type

    def grant_delegated_permissions(self, app_id: str, scope: AppRole | str) -> Self:
        """Grants a delegated permission (AllPrincipals) to the client app on this resource.
        Creates a new grant or updates an existing one if already present."""

        scope_val = scope.value if isinstance(scope, AppRole) else scope

        def _find_existing(sp):
            self.context.oauth2_permission_grants.get().filter(
                f"clientId eq '{sp.id}' and consentType eq 'AllPrincipals'"
            ).after_execute(lambda grants: _handle_grant(sp.id, grants))

        def _handle_grant(client_sp_id, grants):
            existing_grant = next((g for g in grants if g.resource_id == self.id), None)
            if existing_grant is not None:
                scopes = set(existing_grant.scope.split(" ")) if existing_grant.scope else set()
                if scope_val not in scopes:
                    scopes.add(scope_val)
                    existing_grant.set_property("scope", " ".join(sorted(scopes)))
                    existing_grant.update()
            else:
                self.context.oauth2_permission_grants.add(
                    clientId=client_sp_id,
                    consentType="AllPrincipals",
                    resourceId=self.id,
                    scope=scope_val,
                )

        self.ensure_property("id").after_execute(lambda _: _resolve_sp())

        def _resolve_sp():
            self.context.service_principals.get_by_app_id(app_id).get().after_execute(_find_existing)

        return self

    def get_application_permissions(self, app_id: str) -> ClientResult[AppRoleCollection]:
        """Gets application permissions (app roles) assigned to the client app on this resource."""
        return_type = ClientResult(self.context, AppRoleCollection())

        def _get_application_permissions(client_sp_id: str) -> None:
            assigned_role_ids = [a.app_role_id for a in self.app_role_assigned_to if a.principal_id == client_sp_id]
            for role in self.app_roles:
                if role.id in assigned_role_ids:
                    return_type.value.add(role)

        def _resolve_app():
            self.context.service_principals.get_by_app_id(app_id).get().after_execute(
                lambda sp: _get_application_permissions(sp.id)
            )

        self.ensure_properties(["id", "appRoles", "appRoleAssignedTo"]).after_execute(lambda _: _resolve_app())
        return return_type

    def grant_application_permissions(self, app_id: str, app_role: AppRole | str) -> Self:
        """Grants an app role assignment to a client service principal.

        Idempotent: when the client already holds the app role on this resource
        the call is a no-op, so setup code can be safely re-run.

        Args:
            app_id: Application (client) ID of the client app that receives the role.
            app_role: The role to grant, as an ``AppRole`` or its name.
        """

        def _grant(sp: ServicePrincipal, app_role_id: str | None) -> None:
            assert sp.id is not None
            assert app_role_id is not None
            already = any(a.app_role_id == app_role_id and a.principal_id == sp.id for a in self.app_role_assigned_to)
            if not already:
                self.app_role_assigned_to.add(principalId=sp.id, resourceId=self.id, appRoleId=app_role_id)

        def _ensure_client():
            def _after(sp: ServicePrincipal) -> None:
                if isinstance(app_role, AppRole):
                    _grant(sp, app_role.id)
                else:
                    _grant(sp, self.app_roles[app_role].id)

            self.context.service_principals.get_by_app_id(app_id).get().after_execute(_after)

        self.ensure_properties(["id", "appRoles", "appRoleAssignedTo"]).after_execute(lambda _: _ensure_client())
        return self

    def revoke_application_permissions(self, app_id: str, app_role: AppRole | str) -> Self:
        """Revokes an app role assignment from a client service principal.

        Only the assignment whose role matches ``app_role`` is removed, so a
        client that holds several roles on this resource keeps the others.

        Args:
            app_id: Application (client) ID of the client app that holds the role.
            app_role: The role to revoke, as an ``AppRole`` or its name.
        """

        def _revoke(principal_id: str | None, app_role_id: str | None) -> None:
            assert principal_id is not None
            assert app_role_id is not None
            for item in self.app_role_assigned_to:
                if item.principal_id == principal_id and item.app_role_id == app_role_id:
                    assert item.id is not None
                    self.app_role_assigned_to[item.id].delete_object()

        def _ensure_app_role(sp: ServicePrincipal) -> None:
            assert sp.id is not None
            if isinstance(app_role, AppRole):
                _revoke(sp.id, app_role.id)
            else:
                _revoke(sp.id, self.app_roles[app_role].id)

        def _ensure_principal():
            self.context.service_principals.get_by_app_id(app_id).select(["id"]).get().after_execute(_ensure_app_role)

        self.ensure_properties(["id", "appId", "appRoles", "appRoleAssignedTo"]).after_execute(
            lambda _: _ensure_principal()
        )
        return self

    def revoke_delegated_permissions(self, client_id: str, scope: str) -> Self:
        def _revoke(all_grants: OAuth2PermissionGrantCollection) -> None:
            for g in all_grants:
                assert g.scope is not None
                if scope in g.scope.split():
                    g.delete_object()

        def _client_resolved(sp: ServicePrincipal):
            self.context.oauth2_permission_grants.get().filter(f"clientId eq '{sp.id}'").after_execute(_revoke)

        self.context.service_principals.get_by_app_id(client_id).get().after_execute(_client_resolved)
        return self

    def remove_password(self, key_id: str) -> Self:
        """Remove a password from a servicePrincipal object.

        Args:
            key_id (str): The unique identifier for the password.
        """
        qry = ServiceOperationQuery(self, "removePassword", None, {"keyId": key_id})
        self.context.add_query(qry)
        return self

    @property
    def account_enabled(self) -> Optional[bool]:
        """
        true if the service principal account is enabled; otherwise, false. If set to false, then no users will be
        able to sign in to this app, even if they are assigned to it. Supports $filter (eq, ne, not, in).
        """
        return self.properties.get("accountEnabled", None)

    @odata(name="alternativeNames")
    @property
    def alternative_names(self):
        """
        Used to retrieve service principals by subscription, identify resource group and full resource ids for
        managed identities. Supports $filter (eq, not, ge, le, startsWith).
        """
        return self.properties.get("alternativeNames", StringCollection())

    @property
    def app_description(self) -> Optional[str]:
        """
        The description exposed by the associated application.
        """
        return self.properties.get("appDescription", None)

    @property
    def app_display_name(self) -> Optional[str]:
        """The display name exposed by the associated application."""
        return self.properties.get("appDisplayName", None)

    @property
    def app_id(self) -> Optional[str]:
        """The unique identifier for the associated application (its appId property)."""
        return self.properties.get("appId", None)

    def app_role_assignment_required(self) -> Optional[bool]:
        """Specifies whether users or other service principals need to be granted an app role assignment for
        this service principal before users can sign in or apps can get tokens. The default value is false.
        Not nullable."""
        return self.properties.get("appRoleAssignmentRequired", None)

    @odata(name="appRoleAssignedTo")
    @property
    def app_role_assigned_to(self) -> AppRoleAssignmentCollection:
        """
        App role assignments for this app or service, granted to users, groups, and other service principals.
        Supports $expand."""
        return self.properties.get(
            "appRoleAssignedTo",
            AppRoleAssignmentCollection(self.context, ResourcePath("appRoleAssignedTo", self.resource_path)),
        )

    @odata(name="appRoleAssignments")
    @property
    def app_role_assignments(self) -> AppRoleAssignmentCollection:
        """Get an event collection or an appRoleAssignments."""
        return self.properties.get(
            "appRoleAssignments",
            AppRoleAssignmentCollection(self.context, ResourcePath("appRoleAssignments", self.resource_path)),
        )

    @odata(name="appRoles")
    @property
    def app_roles(self):
        """The roles exposed by the application which this service principal represents."""
        return self.properties.get("appRoles", AppRoleCollection())

    @property
    def display_name(self) -> Optional[str]:
        """The display name."""
        return self.properties.get("displayName", None)

    @property
    def homepage(self) -> Optional[str]:
        """Home page or landing page of the application"""
        return self.properties.get("homepage", None)

    @odata(name="keyCredentials")
    @property
    def key_credentials(self) -> ClientValueCollection[KeyCredential]:
        """
        The collection of key credentials associated with the service principal. Not nullable.
        Supports $filter (eq, not, ge, le).
        """
        return self.properties.setdefault("keyCredentials", ClientValueCollection(KeyCredential))

    @odata(name="passwordCredentials")
    @property
    def password_credentials(self) -> ClientValueCollection[PasswordCredential]:
        """
        The collection of password credentials associated with the service principal. Not nullable.
        Supports $filter (eq, not, ge, le).
        """
        return self.properties.setdefault("passwordCredentials", ClientValueCollection(PasswordCredential))

    @property
    def login_url(self) -> Optional[str]:
        """
        Specifies the URL where the service provider redirects the user to Azure AD to authenticate.
        Azure AD uses the URL to launch the application from Microsoft 365 or the Azure AD My Apps. When blank,
        Azure AD performs IdP-initiated sign-on for applications configured with SAML-based single sign-on.
        The user launches the application from Microsoft 365, the Azure AD My Apps, or the Azure AD SSO URL.
        """
        return self.properties.get("loginUrl", None)

    @property
    def logout_url(self) -> Optional[str]:
        """
        Specifies the URL that will be used by Microsoft's authorization service to logout an user using
        OpenId Connect front-channel, back-channel or SAML logout protocols.
        """
        return self.properties.get("logoutUrl", None)

    @odata(name="notificationEmailAddresses")
    @property
    def notification_email_addresses(self) -> StringCollection:
        """
        Specifies the list of email addresses where Azure AD sends a notification when the active certificate is near
        the expiration date. This is only for the certificates used to sign the SAML token issued for Azure
        AD Gallery applications.
        """
        return self.properties.get("notificationEmailAddresses", StringCollection())

    @property
    def service_principal_type(self) -> Optional[str]:
        """
        Identifies whether the service principal represents an application, a managed identity, or a legacy application.
        This is set by Azure AD internally. The servicePrincipalType property can be set to three different values:
            Application - A service principal that represents an application or service.
            The appId property identifies the associated app registration, and matches the appId of an application,
            possibly from a different tenant. If the associated app registration is missing, tokens are not issued
            for the service principal.

            ManagedIdentity - A service principal that represents a managed identity. Service principals
            representing managed identities can be granted access and permissions, but cannot be updated
            or modified directly.

            Legacy - A service principal that represents an app created before app registrations,
            or through legacy experiences. Legacy service principal can have credentials, service principal names,
            reply URLs, and other properties which are editable by an authorized user,
            but does not have an associated app registration. The appId value does not associate
            the service principal with an app registration.
            The service principal can only be used in the tenant where it was created.
        """
        return self.properties.get("servicePrincipalType", None)

    @property
    def owners(self):
        """Directory objects that are owners of this servicePrincipal.
        The owners are a set of non-admin users or servicePrincipals who are allowed to modify this object.
        """
        return self.properties.get(
            "owners",
            DirectoryObjectCollection(self.context, ResourcePath("owners", self.resource_path)),
        )

    @odata(name="oauth2PermissionScopes")
    @property
    def oauth2_permission_scopes(self) -> ClientValueCollection[PermissionScope]:
        """
        The delegated permissions exposed by the application. For more information see the oauth2PermissionScopes
        property on the application entity's api property.
        """
        return self.properties.get("oauth2PermissionScopes", ClientValueCollection(PermissionScope))

    @odata(name="oauth2PermissionGrants")
    @property
    def oauth2_permission_grants(self) -> DeltaCollection[OAuth2PermissionGrant]:
        """"""
        return self.properties.get(
            "oauth2PermissionGrants",
            DeltaCollection(
                self.context,
                OAuth2PermissionGrant,
                ResourcePath("oauth2PermissionGrants", self.resource_path),
            ),
        )

    @odata(name="createdObjects")
    @property
    def created_objects(self):
        """Directory objects created by this service principal."""
        return self.properties.get(
            "createdObjects",
            DirectoryObjectCollection(self.context, ResourcePath("createdObjects", self.resource_path)),
        )

    @odata(name="ownedObjects")
    @property
    def owned_objects(self):
        """Directory objects that are owned by this service principal."""
        return self.properties.get(
            "ownedObjects",
            DirectoryObjectCollection(self.context, ResourcePath("ownedObjects", self.resource_path)),
        )

    @property
    def synchronization(self) -> Synchronization:
        """
        Represents the capability for Azure Active Directory (Azure AD) identity synchronization through
        the Microsoft Graph API.
        """
        return self.properties.get(
            "synchronization",
            Synchronization(self.context, ResourcePath("synchronization", self.resource_path)),
        )

    @property
    def token_encryption_key_id(self) -> Optional[str]:
        """
        Specifies the keyId of a public key from the keyCredentials collection. When configured, Azure AD issues tokens
        for this application encrypted using the key specified by this property. The application code that receives
        the encrypted token must use the matching private key to decrypt the token before it can be used
        for the signed-in user.
        """
        return self.properties.get("tokenEncryptionKeyId", None)

    def set_property(self, name, value, persist_changes=True):
        if self._resource_path is None and name == "appId":
            assert self.parent_collection is not None
            self._resource_path = AppIdPath(value, self.parent_collection.resource_path)
        return super().set_property(name, value, persist_changes)

    @property
    def entity_type_name(self):
        return "microsoft.graph.ServicePrincipal"

    @property
    def add_ins(self) -> ClientValueCollection[AddIn]:
        """Gets the addIns property"""
        from office365.directory.objects.addin import AddIn

        return self.properties.get("addIns", ClientValueCollection[AddIn](AddIn))

    @property
    def application_template_id(self) -> Optional[str]:
        """Gets the applicationTemplateId property"""
        return self.properties.get("applicationTemplateId", None)

    @property
    def app_owner_organization_id(self) -> Optional[UUID]:
        """Gets the appOwnerOrganizationId property"""
        return self.properties.get("appOwnerOrganizationId", None)

    @property
    def created_by_app_id(self) -> Optional[str]:
        """Gets the createdByAppId property"""
        return self.properties.get("createdByAppId", None)

    @property
    def custom_security_attributes(self) -> CustomSecurityAttributeValue:
        """Gets the customSecurityAttributes property"""
        from office365.directory.objects.customsecurityattributevalue import (
            CustomSecurityAttributeValue,
        )

        return self.properties.get("customSecurityAttributes", CustomSecurityAttributeValue())

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def disabled_by_microsoft_status(self) -> Optional[str]:
        """Gets the disabledByMicrosoftStatus property"""
        return self.properties.get("disabledByMicrosoftStatus", None)

    @property
    def info(self) -> InformationalUrl:
        """Gets the info property"""
        from office365.directory.objects.informationalurl import InformationalUrl

        return self.properties.get("info", InformationalUrl())

    @property
    def is_disabled(self) -> Optional[bool]:
        """Gets the isDisabled property"""
        return self.properties.get("isDisabled", None)

    @property
    def notes(self) -> Optional[str]:
        """Gets the notes property"""
        return self.properties.get("notes", None)

    @property
    def preferred_single_sign_on_mode(self) -> Optional[str]:
        """Gets the preferredSingleSignOnMode property"""
        return self.properties.get("preferredSingleSignOnMode", None)

    @property
    def preferred_token_signing_key_thumbprint(self) -> Optional[str]:
        """Gets the preferredTokenSigningKeyThumbprint property"""
        return self.properties.get("preferredTokenSigningKeyThumbprint", None)

    @property
    def reply_urls(self) -> StringCollection:
        """Gets the replyUrls property"""
        return self.properties.get("replyUrls", StringCollection())

    @property
    def resource_specific_application_permissions(self) -> ClientValueCollection[ResourceSpecificPermission]:
        """Gets the resourceSpecificApplicationPermissions property"""
        from office365.directory.permissions.grants.resourcespecificpermission import (
            ResourceSpecificPermission,
        )

        return self.properties.get(
            "resourceSpecificApplicationPermissions",
            ClientValueCollection[ResourceSpecificPermission](ResourceSpecificPermission),
        )

    @property
    def saml_single_sign_on_settings(self) -> SamlSingleSignOnSettings:
        """Gets the samlSingleSignOnSettings property"""
        from office365.directory.serviceprincipals.samlsinglesignonsettings import (
            SamlSingleSignOnSettings,
        )

        return self.properties.get("samlSingleSignOnSettings", SamlSingleSignOnSettings())

    @property
    def service_principal_names(self) -> StringCollection:
        """Gets the servicePrincipalNames property"""
        return self.properties.get("servicePrincipalNames", StringCollection())

    @property
    def sign_in_audience(self) -> Optional[str]:
        """Gets the signInAudience property"""
        return self.properties.get("signInAudience", None)

    @property
    def tags(self) -> StringCollection:
        """Gets the tags property"""
        return self.properties.get("tags", StringCollection())

    @property
    def verified_publisher(self) -> VerifiedPublisher:
        """Gets the verifiedPublisher property"""
        from office365.directory.applications.verifiedpublisher import VerifiedPublisher

        return self.properties.get("verifiedPublisher", VerifiedPublisher())

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
    def claims_mapping_policies(self) -> EntityCollection[ClaimsMappingPolicy]:
        """Gets the claimsMappingPolicies property"""
        from office365.directory.policies.claims_mapping_policy import (
            ClaimsMappingPolicy,
        )

        return self.properties.get(
            "claimsMappingPolicies",
            EntityCollection[ClaimsMappingPolicy](
                self.context, ClaimsMappingPolicy, ResourcePath("claimsMappingPolicies", self.resource_path)
            ),
        )

    @property
    def delegated_permission_classifications(self) -> EntityCollection[DelegatedPermissionClassification]:
        """Gets the delegatedPermissionClassifications property"""
        from office365.directory.serviceprincipals.delegated_permission_classification import (
            DelegatedPermissionClassification,
        )

        return self.properties.get(
            "delegatedPermissionClassifications",
            EntityCollection[DelegatedPermissionClassification](
                self.context,
                DelegatedPermissionClassification,
                ResourcePath("delegatedPermissionClassifications", self.resource_path),
            ),
        )

    @property
    def endpoints(self) -> EntityCollection[Endpoint]:
        """Gets the endpoints property"""
        from office365.common.endpoint import Endpoint

        return self.properties.get(
            "endpoints",
            EntityCollection[Endpoint](self.context, Endpoint, ResourcePath("endpoints", self.resource_path)),
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
    def member_of(self) -> EntityCollection[DirectoryObject]:
        """Gets the memberOf property"""
        from office365.directory.objects.object import DirectoryObject

        return self.properties.get(
            "memberOf",
            EntityCollection[DirectoryObject](
                self.context, DirectoryObject, ResourcePath("memberOf", self.resource_path)
            ),
        )

    @property
    def remote_desktop_security_configuration(self) -> RemoteDesktopSecurityConfiguration:
        """Gets the remoteDesktopSecurityConfiguration property"""
        from office365.directory.serviceprincipals.remote_desktop_security_configuration import (
            RemoteDesktopSecurityConfiguration,
        )

        return self.properties.get(
            "remoteDesktopSecurityConfiguration",
            RemoteDesktopSecurityConfiguration(
                self.context, ResourcePath("remoteDesktopSecurityConfiguration", self.resource_path)
            ),
        )

    @property
    def token_issuance_policies(self) -> EntityCollection[TokenIssuancePolicy]:
        """Gets the tokenIssuancePolicies property"""
        from office365.directory.policies.token_issuance import TokenIssuancePolicy

        return self.properties.get(
            "tokenIssuancePolicies",
            EntityCollection[TokenIssuancePolicy](
                self.context, TokenIssuancePolicy, ResourcePath("tokenIssuancePolicies", self.resource_path)
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

    @property
    def transitive_member_of(self) -> EntityCollection[DirectoryObject]:
        """Gets the transitiveMemberOf property"""
        from office365.directory.objects.object import DirectoryObject

        return self.properties.get(
            "transitiveMemberOf",
            EntityCollection[DirectoryObject](
                self.context, DirectoryObject, ResourcePath("transitiveMemberOf", self.resource_path)
            ),
        )
