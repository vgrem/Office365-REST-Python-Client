from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.entity import Entity


class RemoteTenantGroup(Entity):
    @property
    def remote_group_display_name(self) -> Optional[str]:
        """Gets the remoteGroupDisplayName property"""
        return self.properties.get("remoteGroupDisplayName", None)

    @property
    def remote_group_id(self) -> Optional[UUID]:
        """Gets the remoteGroupId property"""
        return self.properties.get("remoteGroupId", None)

    @property
    def remote_tenant_display_name(self) -> Optional[str]:
        """Gets the remoteTenantDisplayName property"""
        return self.properties.get("remoteTenantDisplayName", None)

    @property
    def remote_tenant_id(self) -> Optional[UUID]:
        """Gets the remoteTenantId property"""
        return self.properties.get("remoteTenantId", None)

    @property
    def remote_tenant_primary_domain(self) -> Optional[str]:
        """Gets the remoteTenantPrimaryDomain property"""
        return self.properties.get("remoteTenantPrimaryDomain", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RemoteTenantGroup"
