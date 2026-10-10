from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.permissions.identity import Identity
from office365.runtime.client_value import ClientValue


@dataclass
class EngagementIdentitySet(ClientValue):
    audience: Identity = field(default_factory=Identity)
    group: Identity = field(default_factory=Identity)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EngagementIdentitySet"
