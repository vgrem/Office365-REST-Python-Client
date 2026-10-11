from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.permissions.identity import Identity
    from office365.directory.unified_role_management_policy_rule import (
        UnifiedRoleManagementPolicyRule,
    )


class UnifiedRoleManagementPolicy(Entity):
    """Specifies the various policies associated with scopes and roles.
    For policies that apply to Azure RBAC, use the Azure REST PIM API for role management policies.
    """

    def __str__(self):
        return self.display_name or self.entity_type_name

    @property
    def display_name(self) -> Optional[str]:
        """
        Display name for the policy.
        """
        return self.properties.get("displayName", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def is_organization_default(self) -> Optional[bool]:
        """Gets the isOrganizationDefault property"""
        return self.properties.get("isOrganizationDefault", None)

    @property
    def last_modified_by(self) -> Identity:
        """Gets the lastModifiedBy property"""
        from office365.directory.permissions.identity import Identity

        return self.properties.get("lastModifiedBy", Identity())

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def scope_id(self) -> Optional[str]:
        """Gets the scopeId property"""
        return self.properties.get("scopeId", None)

    @property
    def scope_type(self) -> Optional[str]:
        """Gets the scopeType property"""
        return self.properties.get("scopeType", None)

    @property
    def effective_rules(self) -> EntityCollection[UnifiedRoleManagementPolicyRule]:
        """Gets the effectiveRules property"""
        from office365.directory.unified_role_management_policy_rule import (
            UnifiedRoleManagementPolicyRule,
        )

        return self.properties.get(
            "effectiveRules",
            EntityCollection[UnifiedRoleManagementPolicyRule](
                self.context, UnifiedRoleManagementPolicyRule, ResourcePath("effectiveRules", self.resource_path)
            ),
        )

    @property
    def rules(self) -> EntityCollection[UnifiedRoleManagementPolicyRule]:
        """Gets the rules property"""
        from office365.directory.unified_role_management_policy_rule import (
            UnifiedRoleManagementPolicyRule,
        )

        return self.properties.get(
            "rules",
            EntityCollection[UnifiedRoleManagementPolicyRule](
                self.context, UnifiedRoleManagementPolicyRule, ResourcePath("rules", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleManagementPolicy"
