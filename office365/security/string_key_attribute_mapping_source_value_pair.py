from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.security.attribute_mapping_source import AttributeMappingSource


@dataclass
class StringKeyAttributeMappingSourceValuePair(ClientValue):
    key: str | None = None
    value: AttributeMappingSource | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.StringKeyAttributeMappingSourceValuePair"
