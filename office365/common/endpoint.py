from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class Endpoint(Entity):
    @property
    def capability(self) -> Optional[str]:
        """Gets the capability property"""
        return self.properties.get("capability", None)

    @property
    def provider_id(self) -> Optional[str]:
        """Gets the providerId property"""
        return self.properties.get("providerId", None)

    @property
    def provider_name(self) -> Optional[str]:
        """Gets the providerName property"""
        return self.properties.get("providerName", None)

    @property
    def provider_resource_id(self) -> Optional[str]:
        """Gets the providerResourceId property"""
        return self.properties.get("providerResourceId", None)

    @property
    def uri(self) -> Optional[str]:
        """Gets the uri property"""
        return self.properties.get("uri", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Endpoint"
