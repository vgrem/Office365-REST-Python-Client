from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class AllowedValue(Entity):
    @property
    def is_active(self) -> Optional[bool]:
        """Gets the isActive property"""
        return self.properties.get("isActive", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AllowedValue"
