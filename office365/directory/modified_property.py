from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class ModifiedProperty(ClientValue):
    displayName: str | None = None
    newValue: str | None = None
    oldValue: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ModifiedProperty"
