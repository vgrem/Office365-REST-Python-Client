from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.entity import Entity


class Contract(Entity):
    @property
    def contract_type(self) -> Optional[str]:
        """Gets the contractType property"""
        return self.properties.get("contractType", None)

    @property
    def customer_id(self) -> Optional[UUID]:
        """Gets the customerId property"""
        return self.properties.get("customerId", None)

    @property
    def default_domain_name(self) -> Optional[str]:
        """Gets the defaultDomainName property"""
        return self.properties.get("defaultDomainName", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Contract"
