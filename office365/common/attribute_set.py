from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class AttributeSet(Entity):
    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def max_attributes_per_set(self) -> Optional[int]:
        """Gets the maxAttributesPerSet property"""
        return self.properties.get("maxAttributesPerSet", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttributeSet"
