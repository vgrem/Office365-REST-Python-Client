from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


@dataclass
class ContainerFilter(ClientValue):
    includedContainers: StringCollection = field(default_factory=StringCollection)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ContainerFilter"
