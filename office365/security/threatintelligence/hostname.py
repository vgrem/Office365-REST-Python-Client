from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class Hostname(Entity):
    @property
    def registrant(self) -> Optional[str]:
        """Gets the registrant property"""
        return self.properties.get("registrant", None)

    @property
    def registrar(self) -> Optional[str]:
        """Gets the registrar property"""
        return self.properties.get("registrar", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.Hostname"
