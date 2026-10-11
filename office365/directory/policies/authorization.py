from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.directory.permissions.default_user_role import DefaultUserRolePermissions
from office365.directory.policies.base import PolicyBase


class AuthorizationPolicy(PolicyBase):
    """Represents a policy that can control Azure Active Directory authorization settings.
    It's a singleton that inherits from base policy type, and always exists for the tenant.
    """

    @property
    def allowed_to_sign_up_email_based_subscriptions(self) -> Optional[bool]:
        """Indicates whether a user can join the tenant by email validation."""
        return self.properties.get("allowedToSignUpEmailBasedSubscriptions", None)

    @property
    def allowed_to_use_sspr(self) -> Optional[bool]:
        """Indicates whether users can use the Self-Service Password Reset feature on the tenant."""
        return self.properties.get("allowedToUseSSPR", None)

    @property
    def allow_email_verified_users_to_join_organization(self) -> Optional[bool]:
        """Indicates whether a user can join the tenant by email validation."""
        return self.properties.get("allowEmailVerifiedUsersToJoinOrganization", None)

    @property
    def allow_invites_from(self) -> Optional[str]:
        """Indicates who can invite external users to the organization.
        Possible values are: none, adminsAndGuestInviters, adminsGuestInvitersAndAllMembers, everyone.
        everyone is the default setting for all cloud environments except US Government.
        """
        return self.properties.get("allowInvitesFrom", None)

    @property
    def allow_user_consent_for_risky_apps(self) -> Optional[bool]:
        """Indicates whether user consent for risky apps is allowed.
        We recommend keeping allowUserConsentForRiskyApps as false. Default value is false.
        """
        return self.properties.get("allowUserConsentForRiskyApps", None)

    @property
    def block_msol_powershell(self) -> Optional[bool]:
        """To disable the use of MSOL PowerShell, set this property to true. This also disables user-based access to
        the legacy service endpoint used by MSOL PowerShell. This doesn't affect Microsoft Entra Connect
        or Microsoft Graph.
        """
        return self.properties.get("blockMsolPowerShell", None)

    @property
    def default_user_role_permissions(self) -> Optional[DefaultUserRolePermissions]:
        """Specifies certain customizable permissions for default user role."""
        return self.properties.get("defaultUserRolePermissions", DefaultUserRolePermissions())

    @property
    def guest_user_role_id(self) -> Optional[UUID]:
        """Gets the guestUserRoleId property"""
        return self.properties.get("guestUserRoleId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AuthorizationPolicy"
