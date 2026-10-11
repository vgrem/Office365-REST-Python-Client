from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class UnifiedRoleManagementPolicyAuthenticationContextRule(Entity):
    @property
    def claim_value(self) -> Optional[str]:
        """Gets the claimValue property"""
        return self.properties.get("claimValue", None)

    @property
    def is_enabled(self) -> Optional[bool]:
        """Gets the isEnabled property"""
        return self.properties.get("isEnabled", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleManagementPolicyAuthenticationContextRule"
