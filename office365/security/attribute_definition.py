from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.synchronization.attributetype import AttributeType
from office365.directory.synchronization.mutability import Mutability
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.attribute_definition_metadata_entry import AttributeDefinitionMetadataEntry
from office365.security.referenced_object import ReferencedObject
from office365.security.string_key_string_value_pair import StringKeyStringValuePair


@dataclass
class AttributeDefinition(ClientValue):
    anchor: bool | None = None
    apiExpressions: ClientValueCollection[StringKeyStringValuePair] = field(
        default_factory=lambda: ClientValueCollection(StringKeyStringValuePair)
    )
    caseExact: bool | None = None
    defaultValue: str | None = None
    flowNullValues: bool | None = None
    metadata: ClientValueCollection[AttributeDefinitionMetadataEntry] = field(
        default_factory=lambda: ClientValueCollection(AttributeDefinitionMetadataEntry)
    )
    multivalued: bool | None = None
    mutability: Mutability = Mutability.ReadWrite
    name: str | None = None
    referencedObjects: ClientValueCollection[ReferencedObject] = field(
        default_factory=lambda: ClientValueCollection(ReferencedObject)
    )
    required: bool | None = None
    type: AttributeType = AttributeType.String

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttributeDefinition"
