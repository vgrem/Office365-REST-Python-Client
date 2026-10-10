from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from office365.directory.permissions.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue
from office365.teams.teamwork.calleventtype import TeamworkCallEventType


@dataclass
class CallEndedEventMessageDetail(ClientValue):
    callDuration: timedelta | None = None
    callEventType: TeamworkCallEventType = TeamworkCallEventType.call
    callId: str | None = None
    initiator: IdentitySet = field(default_factory=IdentitySet)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CallEndedEventMessageDetail"
