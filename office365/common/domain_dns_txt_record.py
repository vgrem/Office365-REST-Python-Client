from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class DomainDnsTxtRecord(Entity):
    @property
    def text(self) -> Optional[str]:
        """Gets the text property"""
        return self.properties.get("text", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DomainDnsTxtRecord"
