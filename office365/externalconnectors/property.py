from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


@dataclass
class Property(ClientValue):
    aliases: StringCollection = field(default_factory=StringCollection)
    description: str | None = None
    isQueryable: bool | None = None
    isRefinable: bool | None = None
    isRetrievable: bool | None = None
    isSearchable: bool | None = None
    name: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.externalConnectors.Property"
