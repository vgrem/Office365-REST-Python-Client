from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class DetonationChain(ClientValue):
    childNodes: ClientValueCollection[DetonationChain] = field(
        default_factory=lambda: ClientValueCollection(DetonationChain)
    )
    value: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.DetonationChain"
