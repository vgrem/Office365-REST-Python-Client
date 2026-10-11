from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.policies.admin_consent_request import AdminConsentRequestPolicy
from office365.directory.policies.app_management import AppManagementPolicy
from office365.directory.policies.authentication_flows import AuthenticationFlowsPolicy
from office365.directory.policies.authentication_methods import (
    AuthenticationMethodsPolicy,
)
from office365.directory.policies.authentication_strength import (
    AuthenticationStrengthPolicy,
)
from office365.directory.policies.authorization import AuthorizationPolicy
from office365.directory.policies.conditionalaccess.conditional_access import (
    ConditionalAccessPolicy,
)
from office365.directory.policies.crosstenant.access import CrossTenantAccessPolicy
from office365.directory.policies.device_registration import DeviceRegistrationPolicy
from office365.directory.policies.feature_rollout import FeatureRolloutPolicy
from office365.directory.policies.permission_grant import PermissionGrantPolicy
from office365.directory.policies.security_defaults import (
    IdentitySecurityDefaultsEnforcementPolicy,
)
from office365.directory.policies.tenant_app_management import TenantAppManagementPolicy
from office365.directory.policies.unifiedrolemanagement.policy import (
    UnifiedRoleManagementPolicy,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.directory.policies.activity_based_timeout_policy import (
        ActivityBasedTimeoutPolicy,
    )
    from office365.directory.policies.claims_mapping_policy import ClaimsMappingPolicy
    from office365.directory.policies.federated_token_validation_policy import (
        FederatedTokenValidationPolicy,
    )
    from office365.directory.policies.home_realm_discovery import (
        HomeRealmDiscoveryPolicy,
    )
    from office365.directory.policies.ownerless_group_policy import OwnerlessGroupPolicy
    from office365.directory.policies.token_issuance import TokenIssuancePolicy
    from office365.directory.policies.token_lifetime import TokenLifetimePolicy
    from office365.directory.unified_role_management_policy_assignment import (
        UnifiedRoleManagementPolicyAssignment,
    )


class PolicyRoot(Entity):
    """Resource type exposing navigation properties for the policies singleton."""

    @property
    def admin_consent_request_policy(self) -> AdminConsentRequestPolicy:
        """
        The policy by which consent requests are created and managed for the entire tenant.
        """
        return self.properties.get(
            "adminConsentRequestPolicy",
            AdminConsentRequestPolicy(
                self.context,
                ResourcePath("adminConsentRequestPolicy", self.resource_path),
            ),
        )

    @property
    def authentication_methods_policy(self) -> AuthenticationMethodsPolicy:
        """
        The authentication methods and the users that are allowed to use them to sign in and perform multi-factor
        authentication (MFA) in Azure Active Directory (Azure AD).
        """
        return self.properties.get(
            "authenticationMethodsPolicy",
            AuthenticationMethodsPolicy(
                self.context,
                ResourcePath("authenticationMethodsPolicy", self.resource_path),
            ),
        )

    @property
    def authentication_strength_policies(
        self,
    ) -> EntityCollection[AuthenticationStrengthPolicy]:
        """
        The authentication method combinations that are to be used in scenarios defined by Azure AD Conditional Access.
        """
        return self.properties.get(
            "authenticationStrengthPolicies",
            EntityCollection(
                self.context,
                AuthenticationStrengthPolicy,
                ResourcePath("authenticationStrengthPolicies", self.resource_path),
            ),
        )

    @property
    def authentication_flows_policy(self) -> AuthenticationFlowsPolicy:
        """The policy configuration of the self-service sign-up experience of external users."""
        return self.properties.get(
            "authenticationFlowsPolicy",
            AuthenticationFlowsPolicy(
                self.context,
                ResourcePath("authenticationFlowsPolicy", self.resource_path),
            ),
        )

    @property
    def authorization_policy(self) -> AuthorizationPolicy:
        """The policy that controls Azure AD authorization settings."""
        return self.properties.get(
            "authorizationPolicy",
            AuthorizationPolicy(self.context, ResourcePath("authorizationPolicy", self.resource_path)),
        )

    @property
    def app_management_policies(self) -> EntityCollection[AppManagementPolicy]:
        """The policies that enforce app management restrictions for specific applications and service principals,
        overriding the defaultAppManagementPolicy."""
        return self.properties.get(
            "appManagementPolicies",
            EntityCollection(
                self.context,
                AppManagementPolicy,
                ResourcePath("appManagementPolicies", self.resource_path),
            ),
        )

    @property
    def conditional_access_policies(self) -> EntityCollection[ConditionalAccessPolicy]:
        """The custom rules that define an access scenario"""
        return self.properties.get(
            "conditionalAccessPolicies",
            EntityCollection(
                self.context,
                ConditionalAccessPolicy,
                ResourcePath("conditionalAccessPolicies", self.resource_path),
            ),
        )

    @property
    def cross_tenant_access_policy(self) -> CrossTenantAccessPolicy:
        """
        The custom rules that define an access scenario when interacting with external Azure AD tenants.
        """
        return self.properties.get(
            "crossTenantAccessPolicy",
            CrossTenantAccessPolicy(
                self.context,
                ResourcePath("crossTenantAccessPolicy", self.resource_path),
            ),
        )

    @property
    def device_registration_policy(self) -> DeviceRegistrationPolicy:
        """ """
        return self.properties.get(
            "deviceRegistrationPolicy",
            DeviceRegistrationPolicy(
                self.context,
                ResourcePath("deviceRegistrationPolicy", self.resource_path),
            ),
        )

    @odata(name="identitySecurityDefaultsEnforcementPolicy")
    @property
    def identity_security_defaults_enforcement_policy(self) -> IdentitySecurityDefaultsEnforcementPolicy:
        """The tenant-wide policy that controls Microsoft Entra security defaults."""
        return self.properties.get(
            "identitySecurityDefaultsEnforcementPolicy",
            IdentitySecurityDefaultsEnforcementPolicy(
                self.context,
                ResourcePath("identitySecurityDefaultsEnforcementPolicy", self.resource_path),
            ),
        )

    @odata(name="defaultAppManagementPolicy")
    @property
    def default_app_management_policy(self) -> TenantAppManagementPolicy:
        """
        The tenant-wide policy that enforces app management restrictions for all applications and service principals.
        """
        return self.properties.get(
            "defaultAppManagementPolicy",
            TenantAppManagementPolicy(
                self.context,
                ResourcePath("defaultAppManagementPolicy", self.resource_path),
            ),
        )

    @odata(name="featureRolloutPolicies")
    @property
    def feature_rollout_policies(self) -> EntityCollection[FeatureRolloutPolicy]:
        """The feature rollout policy associated with a directory object."""
        return self.properties.get(
            "featureRolloutPolicies",
            EntityCollection(
                self.context,
                FeatureRolloutPolicy,
                ResourcePath("featureRolloutPolicies", self.resource_path),
            ),
        )

    @odata(name="permissionGrantPolicies")
    @property
    def permission_grant_policies(self) -> EntityCollection[PermissionGrantPolicy]:
        """
        The policy that specifies the conditions under which consent can be granted.
        """
        return self.properties.get(
            "permissionGrantPolicies",
            EntityCollection(
                self.context,
                PermissionGrantPolicy,
                ResourcePath("permissionGrantPolicies", self.resource_path),
            ),
        )

    @odata(name="roleManagementPolicies")
    @property
    def role_management_policies(self) -> EntityCollection[UnifiedRoleManagementPolicy]:
        """Specifies the various policies associated with scopes and roles."""
        return self.properties.get(
            "roleManagementPolicies",
            EntityCollection(
                self.context,
                UnifiedRoleManagementPolicy,
                ResourcePath("roleManagementPolicies", self.resource_path),
            ),
        )

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "adminConsentRequestPolicy": self.admin_consent_request_policy,
                "authenticationStrengthPolicies": self.authentication_strength_policies,
                "authenticationFlowsPolicy": self.authentication_flows_policy,
                "appManagementPolicies": self.app_management_policies,
                "authenticationMethodsPolicy": self.authentication_methods_policy,
                "authorizationPolicy": self.authorization_policy,
                "conditional_access_policies": self.conditional_access_policies,
                "crossTenantAccessPolicy": self.cross_tenant_access_policy,
                "deviceRegistrationPolicy": self.device_registration_policy,
            }
            default_value = property_mapping.get(name, None)
        return super().get_property(name, default_value)

    @property
    def activity_based_timeout_policies(self) -> EntityCollection[ActivityBasedTimeoutPolicy]:
        """Gets the activityBasedTimeoutPolicies property"""
        from office365.directory.policies.activity_based_timeout_policy import (
            ActivityBasedTimeoutPolicy,
        )

        return self.properties.get(
            "activityBasedTimeoutPolicies",
            EntityCollection[ActivityBasedTimeoutPolicy](
                self.context,
                ActivityBasedTimeoutPolicy,
                ResourcePath("activityBasedTimeoutPolicies", self.resource_path),
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
    def federated_token_validation_policy(self) -> FederatedTokenValidationPolicy:
        """Gets the federatedTokenValidationPolicy property"""
        from office365.directory.policies.federated_token_validation_policy import (
            FederatedTokenValidationPolicy,
        )

        return self.properties.get(
            "federatedTokenValidationPolicy",
            FederatedTokenValidationPolicy(
                self.context, ResourcePath("federatedTokenValidationPolicy", self.resource_path)
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
    def ownerless_group_policy(self) -> OwnerlessGroupPolicy:
        """Gets the ownerlessGroupPolicy property"""
        from office365.directory.policies.ownerless_group_policy import (
            OwnerlessGroupPolicy,
        )

        return self.properties.get(
            "ownerlessGroupPolicy",
            OwnerlessGroupPolicy(self.context, ResourcePath("ownerlessGroupPolicy", self.resource_path)),
        )

    @property
    def role_management_policy_assignments(self) -> EntityCollection[UnifiedRoleManagementPolicyAssignment]:
        """Gets the roleManagementPolicyAssignments property"""
        from office365.directory.unified_role_management_policy_assignment import (
            UnifiedRoleManagementPolicyAssignment,
        )

        return self.properties.get(
            "roleManagementPolicyAssignments",
            EntityCollection[UnifiedRoleManagementPolicyAssignment](
                self.context,
                UnifiedRoleManagementPolicyAssignment,
                ResourcePath("roleManagementPolicyAssignments", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PolicyRoot"
