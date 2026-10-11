from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.search.identity import Identity


@dataclass
class IdentitySet(ClientValue):
    """Represents a keyed collection of identity resources. It is used to represent a set of
    identities associated with various events for an item, such as created by or last modified by.
    """

    @property
    def entity_type_name(self):
        return "microsoft.graph.search.identitySet"

    application: Identity = field(default_factory=Identity)

    device: Identity = field(default_factory=Identity)

    user: Identity = field(default_factory=Identity)
