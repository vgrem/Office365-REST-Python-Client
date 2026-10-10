from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.permissions.identity import Identity
from office365.runtime.client_value import ClientValue


@dataclass
class IdentitySet(ClientValue):
    application: Identity = field(default_factory=Identity)

    device: Identity = field(default_factory=Identity)

    user: Identity = field(default_factory=Identity)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IdentitySet"
