from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.attribute_mapping import AttributeMapping
from office365.directory.security.filter import Filter
from office365.directory.synchronization.objectflowtypes import ObjectFlowTypes
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class ObjectMapping(ClientValue):
    attributeMappings: ClientValueCollection[AttributeMapping] = field(
        default_factory=lambda: ClientValueCollection(AttributeMapping)
    )
    enabled: bool | None = None
    flowTypes: ObjectFlowTypes = ObjectFlowTypes.None_
    name: str | None = None
    scope: Filter = field(default_factory=Filter)
    sourceObjectName: str | None = None
    targetObjectName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ObjectMapping"
