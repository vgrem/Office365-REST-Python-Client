from __future__ import annotations

from dataclasses import dataclass, field

from office365.communications.callrecords.user_agent import UserAgent
from office365.runtime.client_value import ClientValue


@dataclass
class Endpoint(ClientValue):
    """Represents an endpoint in a call. The endpoint could be a user's device, a meeting, an application/bot, etc.
    The participantEndpoint and serviceEndpoint types inherit from this type."""

    userAgent: UserAgent = field(default_factory=UserAgent)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.Endpoint"
