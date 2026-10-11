from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.security.datasecurity.policy_location import PolicyLocation


@dataclass
class ProtectedApplicationMetadata(ClientValue):
    applicationLocation: PolicyLocation = field(default_factory=PolicyLocation)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ProtectedApplicationMetadata"
