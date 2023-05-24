from office365.directory.policies.authentication_methods import AuthenticationMethodsPolicy
from office365.directory.policies.permission_grant import PermissionGrantPolicy
from office365.directory.policies.authorization import AuthorizationPolicy
from office365.directory.policies.conditional_access import ConditionalAccessPolicy
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath


class PolicyRoot(Entity):
    """Resource type exposing navigation properties for the policies singleton."""

    @property
    def authentication_methods_policy(self):
        """
        The authentication methods and the users that are allowed to use them to sign in and perform multi-factor
        authentication (MFA) in Azure Active Directory (Azure AD).
        """
        return self.properties.get('authenticationMethodsPolicy',
                                   AuthenticationMethodsPolicy(self.context,
                                                               ResourcePath("authenticationMethodsPolicy",
                                                                            self.resource_path)))

    @property
    def authorization_policy(self):
        """The policy that controls Azure AD authorization settings."""
        return self.properties.get('authorizationPolicy',
                                   AuthorizationPolicy(self.context,
                                                       ResourcePath("authorizationPolicy", self.resource_path)))

    @property
    def app_management_policies(self):
        """The policies that enforce app management restrictions for specific applications and service principals,
        overriding the defaultAppManagementPolicy."""
        return self.properties.get('appManagementPolicies',
                                   AuthorizationPolicy(self.context,
                                                       ResourcePath("appManagementPolicies", self.resource_path)))

    @property
    def permission_grant_policies(self):
        """"
        The policy that specifies the conditions under which consent can be granted.
        """
        return self.properties.get('permissionGrantPolicies',
                                   EntityCollection(self.context, PermissionGrantPolicy,
                                                    ResourcePath("permissionGrantPolicies", self.resource_path)))

    @property
    def conditional_access_policies(self):
        """"
        The custom rules that define an access scenario.
        """
        return self.properties.get('conditionalAccessPolicies',
                                   EntityCollection(self.context, ConditionalAccessPolicy,
                                                    ResourcePath("conditionalAccessPolicies", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "appManagementPolicies": self.app_management_policies,
                "authenticationMethodsPolicy": self.authentication_methods_policy,
                "authorizationPolicy": self.authorization_policy,
                "conditional_access_policies": self.conditional_access_policies,
                "permissionGrantPolicies": self.permission_grant_policies,
            }
            default_value = property_mapping.get(name, None)
        return super(PolicyRoot, self).get_property(name, default_value)
