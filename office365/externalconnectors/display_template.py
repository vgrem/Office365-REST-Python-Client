from __future__ import annotations

from dataclasses import dataclass, field

from office365.externalconnectors.property_rule import PropertyRule
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.json import Json


@dataclass
class DisplayTemplate(ClientValue):
    id: str | None = None
    layout: Json = field(default_factory=Json)
    priority: int | None = None
    rules: ClientValueCollection[PropertyRule] = field(default_factory=lambda: ClientValueCollection(PropertyRule))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.externalConnectors.DisplayTemplate"
