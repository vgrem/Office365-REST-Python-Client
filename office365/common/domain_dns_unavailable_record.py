from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class DomainDnsUnavailableRecord(Entity):
    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DomainDnsUnavailableRecord"
