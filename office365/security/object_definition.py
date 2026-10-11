from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection
from office365.security.attribute_definition import AttributeDefinition
from office365.security.object_definition_metadata_entry import ObjectDefinitionMetadataEntry


@dataclass
class ObjectDefinition(ClientValue):
    attributes: ClientValueCollection[AttributeDefinition] = field(
        default_factory=lambda: ClientValueCollection(AttributeDefinition)
    )
    metadata: ClientValueCollection[ObjectDefinitionMetadataEntry] = field(
        default_factory=lambda: ClientValueCollection(ObjectDefinitionMetadataEntry)
    )
    name: str | None = None
    supportedApis: StringCollection = field(default_factory=StringCollection)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ObjectDefinition"
