from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class ExternalAuthenticationMethod(Entity):
    @property
    def configuration_id(self) -> Optional[str]:
        """Gets the configurationId property"""
        return self.properties.get("configurationId", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ExternalAuthenticationMethod"
