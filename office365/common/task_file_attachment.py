from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class TaskFileAttachment(Entity):
    @property
    def content_bytes(self) -> Optional[bytes]:
        """Gets the contentBytes property"""
        return self.properties.get("contentBytes", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TaskFileAttachment"
