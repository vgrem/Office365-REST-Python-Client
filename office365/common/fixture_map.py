from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class FixtureMap(Entity):
    @property
    def place_id(self) -> Optional[str]:
        """Gets the placeId property"""
        return self.properties.get("placeId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.FixtureMap"
