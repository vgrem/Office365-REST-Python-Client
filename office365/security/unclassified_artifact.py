from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class UnclassifiedArtifact(Entity):
    @property
    def kind(self) -> Optional[str]:
        """Gets the kind property"""
        return self.properties.get("kind", None)

    @property
    def value(self) -> Optional[str]:
        """Gets the value property"""
        return self.properties.get("value", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.UnclassifiedArtifact"
