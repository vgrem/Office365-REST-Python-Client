from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class RelatedTenantsRefreshRequest(Entity):
    @property
    def location(self) -> Optional[str]:
        """Gets the location property"""
        return self.properties.get("location", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RelatedTenantsRefreshRequest"
