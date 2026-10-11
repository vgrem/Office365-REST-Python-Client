from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.policies.azure_ad_registration_policy import (
        AzureADRegistrationPolicy,
    )
    from office365.directory.policies.multifactorauthconfiguration import (
        MultiFactorAuthConfiguration,
    )
    from office365.intune.policies.azure_ad_join_policy import AzureADJoinPolicy
    from office365.intune.policies.local_admin_password_settings import (
        LocalAdminPasswordSettings,
    )


class DeviceRegistrationPolicy(Entity):
    """Represents the policy scope that controls quota restrictions, additional authentication, and authorization
    policies to register device identities to your organization."""

    @property
    def azure_ad_join(self) -> AzureADJoinPolicy:
        """Gets the azureADJoin property"""
        from office365.intune.policies.azure_ad_join_policy import AzureADJoinPolicy

        return self.properties.get("azureADJoin", AzureADJoinPolicy())

    @property
    def azure_ad_registration(self) -> AzureADRegistrationPolicy:
        """Gets the azureADRegistration property"""
        from office365.directory.policies.azure_ad_registration_policy import (
            AzureADRegistrationPolicy,
        )

        return self.properties.get("azureADRegistration", AzureADRegistrationPolicy())

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def local_admin_password(self) -> LocalAdminPasswordSettings:
        """Gets the localAdminPassword property"""
        from office365.intune.policies.local_admin_password_settings import (
            LocalAdminPasswordSettings,
        )

        return self.properties.get("localAdminPassword", LocalAdminPasswordSettings())

    @property
    def multi_factor_auth_configuration(self) -> MultiFactorAuthConfiguration:
        """Gets the multiFactorAuthConfiguration property"""
        from office365.directory.policies.multifactorauthconfiguration import (
            MultiFactorAuthConfiguration,
        )

        return self.properties.get("multiFactorAuthConfiguration", MultiFactorAuthConfiguration.notRequired)

    @property
    def user_device_quota(self) -> Optional[int]:
        """Gets the userDeviceQuota property"""
        return self.properties.get("userDeviceQuota", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceRegistrationPolicy"
