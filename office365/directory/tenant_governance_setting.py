from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class TenantGovernanceSetting(Entity):
    @property
    def can_receive_invitations(self) -> Optional[bool]:
        """Gets the canReceiveInvitations property"""
        return self.properties.get("canReceiveInvitations", None)

    @property
    def is_related_tenants_enabled(self) -> Optional[bool]:
        """Gets the isRelatedTenantsEnabled property"""
        return self.properties.get("isRelatedTenantsEnabled", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TenantGovernanceSetting"
