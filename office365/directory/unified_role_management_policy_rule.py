from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.unified_role_management_policy_rule_target import (
        UnifiedRoleManagementPolicyRuleTarget,
    )


class UnifiedRoleManagementPolicyRule(Entity):
    @property
    def target(self) -> UnifiedRoleManagementPolicyRuleTarget:
        """Gets the target property"""
        from office365.directory.unified_role_management_policy_rule_target import (
            UnifiedRoleManagementPolicyRuleTarget,
        )

        return self.properties.get("target", UnifiedRoleManagementPolicyRuleTarget())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleManagementPolicyRule"
