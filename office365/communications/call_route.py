from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from office365.directory.permissions.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.communications.calls.routingtype import RoutingType


@dataclass
class CallRoute(ClientValue):
    final: IdentitySet = field(default_factory=IdentitySet)
    original: IdentitySet = field(default_factory=IdentitySet)
    routingType: RoutingType = RoutingType.forwarded

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CallRoute"
