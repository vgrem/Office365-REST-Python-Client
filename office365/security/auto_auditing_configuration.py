from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class AutoAuditingConfiguration(Entity):
    @property
    def is_automatic(self) -> Optional[bool]:
        """Gets the isAutomatic property"""
        return self.properties.get("isAutomatic", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AutoAuditingConfiguration"
