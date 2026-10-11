from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class PrintServiceEndpoint(Entity):
    """Represents URI and identifying information for a print service instance."""

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def uri(self) -> Optional[str]:
        """Gets the uri property"""
        return self.properties.get("uri", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrintServiceEndpoint"
