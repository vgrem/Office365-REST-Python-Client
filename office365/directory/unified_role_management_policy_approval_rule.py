from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.approval_settings import ApprovalSettings


class UnifiedRoleManagementPolicyApprovalRule(Entity):
    @property
    def setting(self) -> ApprovalSettings:
        """Gets the setting property"""
        from office365.directory.approval_settings import ApprovalSettings

        return self.properties.get("setting", ApprovalSettings())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleManagementPolicyApprovalRule"
