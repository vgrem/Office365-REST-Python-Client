from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class NetworkAdapter(Entity):
    @property
    def is_enabled(self) -> Optional[bool]:
        """Gets the isEnabled property"""
        return self.properties.get("isEnabled", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the name property"""
        return self.properties.get("name", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.NetworkAdapter"
