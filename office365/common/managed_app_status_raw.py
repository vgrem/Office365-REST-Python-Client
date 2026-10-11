from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.runtime.types.json import Json


class ManagedAppStatusRaw(Entity):
    @property
    def content(self) -> Json:
        """Gets the content property"""
        from office365.runtime.types.json import Json

        return self.properties.get("content", Json())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ManagedAppStatusRaw"
