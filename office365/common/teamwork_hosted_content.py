from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class TeamworkHostedContent(Entity):
    @property
    def content_bytes(self) -> Optional[bytes]:
        """Gets the contentBytes property"""
        return self.properties.get("contentBytes", None)

    @property
    def content_type(self) -> Optional[str]:
        """Gets the contentType property"""
        return self.properties.get("contentType", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TeamworkHostedContent"
