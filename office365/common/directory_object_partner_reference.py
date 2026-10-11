from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.entity import Entity


class DirectoryObjectPartnerReference(Entity):
    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def external_partner_tenant_id(self) -> Optional[UUID]:
        """Gets the externalPartnerTenantId property"""
        return self.properties.get("externalPartnerTenantId", None)

    @property
    def object_type(self) -> Optional[str]:
        """Gets the objectType property"""
        return self.properties.get("objectType", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DirectoryObjectPartnerReference"
