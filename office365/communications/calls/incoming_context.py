from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.permissions.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue


@dataclass
class IncomingContext(ClientValue):
    """Represents the context associated with an incoming call."""

    observedParticipantId: str | None = None

    onBehalfOf: IdentitySet = field(default_factory=IdentitySet)

    sourceParticipantId: str | None = None

    transferor: IdentitySet = field(default_factory=IdentitySet)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IncomingContext"
