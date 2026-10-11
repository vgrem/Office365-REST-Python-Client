from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.policies.base import PolicyBase
from office365.directory.policies.template import PolicyTemplate
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.common.cross_tenant_access_policy_configuration_default import (
        CrossTenantAccessPolicyConfigurationDefault,
    )
    from office365.common.cross_tenant_access_policy_configuration_partner import (
        CrossTenantAccessPolicyConfigurationPartner,
    )


class CrossTenantAccessPolicy(PolicyBase):
    """Represents the base policy in the directory for cross-tenant access settings."""

    @property
    def allowed_cloud_endpoints(self) -> StringCollection:
        """
        Used to specify which Microsoft clouds an organization would like to collaborate with. By default, this value
        is empty. Supported values for this field are: microsoftonline.com, microsoftonline.us,
        and partner.microsoftonline.cn.
        """
        return self.properties.get("allowedCloudEndpoints", StringCollection())

    def templates(self) -> PolicyTemplate:
        """Represents the base policy in the directory for multitenant organization settings."""
        return self.properties.get(
            "templates",
            PolicyTemplate(
                self.context,
                ResourcePath("templates", self.resource_path),
            ),
        )

    @property
    def default(self) -> CrossTenantAccessPolicyConfigurationDefault:
        """Gets the default property"""
        from office365.common.cross_tenant_access_policy_configuration_default import (
            CrossTenantAccessPolicyConfigurationDefault,
        )

        return self.properties.get(
            "default",
            CrossTenantAccessPolicyConfigurationDefault(self.context, ResourcePath("default", self.resource_path)),
        )

    @property
    def partners(self) -> EntityCollection[CrossTenantAccessPolicyConfigurationPartner]:
        """Gets the partners property"""
        from office365.common.cross_tenant_access_policy_configuration_partner import (
            CrossTenantAccessPolicyConfigurationPartner,
        )

        return self.properties.get(
            "partners",
            EntityCollection[CrossTenantAccessPolicyConfigurationPartner](
                self.context, CrossTenantAccessPolicyConfigurationPartner, ResourcePath("partners", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CrossTenantAccessPolicy"
