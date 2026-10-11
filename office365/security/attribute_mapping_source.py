from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.directory.synchronization.attributemappingsourcetype import AttributeMappingSourceType
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.security.string_key_attribute_mapping_source_value_pair import (
        StringKeyAttributeMappingSourceValuePair,
    )


@dataclass
class AttributeMappingSource(ClientValue):
    expression: str | None = None
    name: str | None = None
    parameters: ClientValueCollection[StringKeyAttributeMappingSourceValuePair] | None = None
    type: AttributeMappingSourceType = AttributeMappingSourceType.Attribute

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttributeMappingSource"
