from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class ResourceOperation(Entity):
    @property
    def action_name(self) -> Optional[str]:
        """Gets the actionName property"""
        return self.properties.get("actionName", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def resource_name(self) -> Optional[str]:
        """Gets the resourceName property"""
        return self.properties.get("resourceName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ResourceOperation"
