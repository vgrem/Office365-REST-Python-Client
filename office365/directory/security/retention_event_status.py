from __future__ import annotations

from dataclasses import dataclass

from office365.directory.security.triggers.eventstatustype import EventStatusType
from office365.runtime.client_value import ClientValue


@dataclass
class RetentionEventStatus(ClientValue):
    status: EventStatusType = EventStatusType.pending

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.RetentionEventStatus"
