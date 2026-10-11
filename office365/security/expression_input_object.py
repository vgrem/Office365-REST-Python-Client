from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.object_definition import ObjectDefinition
from office365.security.string_key_object_value_pair import StringKeyObjectValuePair


@dataclass
class ExpressionInputObject(ClientValue):
    definition: ObjectDefinition = field(default_factory=ObjectDefinition)
    properties: ClientValueCollection[StringKeyObjectValuePair] = field(
        default_factory=lambda: ClientValueCollection(StringKeyObjectValuePair)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ExpressionInputObject"
