from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.policies.unifiedrolemanagement.policy import (
        UnifiedRoleManagementPolicy,
    )


class UnifiedRoleManagementPolicyAssignment(Entity):
    @property
    def policy_id(self) -> Optional[str]:
        """Gets the policyId property"""
        return self.properties.get("policyId", None)

    @property
    def role_definition_id(self) -> Optional[str]:
        """Gets the roleDefinitionId property"""
        return self.properties.get("roleDefinitionId", None)

    @property
    def scope_id(self) -> Optional[str]:
        """Gets the scopeId property"""
        return self.properties.get("scopeId", None)

    @property
    def scope_type(self) -> Optional[str]:
        """Gets the scopeType property"""
        return self.properties.get("scopeType", None)

    @property
    def policy(self) -> UnifiedRoleManagementPolicy:
        """Gets the policy property"""
        from office365.directory.policies.unifiedrolemanagement.policy import (
            UnifiedRoleManagementPolicy,
        )

        return self.properties.get(
            "policy", UnifiedRoleManagementPolicy(self.context, ResourcePath("policy", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleManagementPolicyAssignment"
