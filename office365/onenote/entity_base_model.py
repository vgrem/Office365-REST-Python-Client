from __future__ import annotations

from typing import Optional

from office365.entity import Entity
from office365.runtime.paths.builder import ODataPathBuilder


class OnenoteEntityBaseModel(Entity):
    """This is the base type for OneNote entities."""

    def set_property(self, name, value, persist_changes=True):
        super().set_property(name, value, persist_changes)
        if name == "self" and self.resource_url != value:
            # Fallback to canonical path
            path_str = value.replace(self.context.service_root_url, "")
            self._resource_path = ODataPathBuilder.parse_url(path_str)
        return self

    @property
    def self(self) -> Optional[str]:
        """Gets the self property"""
        return self.properties.get("self", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnenoteEntityBaseModel"
