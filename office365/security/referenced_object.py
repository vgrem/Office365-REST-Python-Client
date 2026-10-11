from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class ReferencedObject(ClientValue):
    referencedObjectName: str | None = None
    referencedProperty: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ReferencedObject"
