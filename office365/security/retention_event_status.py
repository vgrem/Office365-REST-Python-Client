from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.types.public_error import PublicError
from office365.security.triggers.eventstatustype import EventStatusType


@dataclass
class RetentionEventStatus(ClientValue):
    status: EventStatusType = EventStatusType.pending

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.RetentionEventStatus"

    error: PublicError = field(default_factory=PublicError)
