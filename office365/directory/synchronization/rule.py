from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.container_filter import ContainerFilter
from office365.security.group_filter import GroupFilter
from office365.security.object_mapping import ObjectMapping
from office365.security.string_key_string_value_pair import StringKeyStringValuePair


@dataclass
class SynchronizationRule(ClientValue):
    containerFilter: ContainerFilter = field(default_factory=ContainerFilter)
    editable: bool | None = None
    groupFilter: GroupFilter = field(default_factory=GroupFilter)
    id: str | None = None
    metadata: ClientValueCollection[StringKeyStringValuePair] = field(
        default_factory=lambda: ClientValueCollection(StringKeyStringValuePair)
    )
    name: str | None = None
    objectMappings: ClientValueCollection[ObjectMapping] = field(
        default_factory=lambda: ClientValueCollection(ObjectMapping)
    )
    priority: int | None = None
    sourceDirectoryName: str | None = None
    targetDirectoryName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SynchronizationRule"
