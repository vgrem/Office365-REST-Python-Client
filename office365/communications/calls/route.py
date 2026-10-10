from __future__ import annotations

from dataclasses import dataclass, field

from office365.communications.calls.routingtype import RoutingType
from office365.directory.permissions.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue


@dataclass
class CallRoute(ClientValue):
    """Represents the call route type."""

    final: IdentitySet = field(default_factory=IdentitySet)

    original: IdentitySet = field(default_factory=IdentitySet)

    routingType: RoutingType = RoutingType.forwarded

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CallRoute"
