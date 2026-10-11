from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.directory.policies.base import PolicyBase

if TYPE_CHECKING:
    from office365.directory.policies.app_management_application_configuration import (
        AppManagementApplicationConfiguration,
    )
    from office365.directory.policies.app_management_service_principal_configuration import (
        AppManagementServicePrincipalConfiguration,
    )


class TenantAppManagementPolicy(PolicyBase):
    """
    Tenant-wide application authentication method policy to enforce app management restrictions for all applications
    and service principals. This policy applies to all apps and service principals unless overridden when an
    appManagementPolicy is applied to the object.
    """

    @property
    def application_restrictions(self) -> AppManagementApplicationConfiguration:
        """Gets the applicationRestrictions property"""
        from office365.directory.policies.app_management_application_configuration import (
            AppManagementApplicationConfiguration,
        )

        return self.properties.get("applicationRestrictions", AppManagementApplicationConfiguration())

    @property
    def is_enabled(self) -> Optional[bool]:
        """Gets the isEnabled property"""
        return self.properties.get("isEnabled", None)

    @property
    def service_principal_restrictions(self) -> AppManagementServicePrincipalConfiguration:
        """Gets the servicePrincipalRestrictions property"""
        from office365.directory.policies.app_management_service_principal_configuration import (
            AppManagementServicePrincipalConfiguration,
        )

        return self.properties.get("servicePrincipalRestrictions", AppManagementServicePrincipalConfiguration())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TenantAppManagementPolicy"
