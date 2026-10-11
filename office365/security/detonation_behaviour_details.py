from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class DetonationBehaviourDetails(ClientValue):
    actionStatus: str | None = None
    behaviourCapability: str | None = None
    behaviourGroup: str | None = None
    details: str | None = None
    eventDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    operation: str | None = None
    processId: str | None = None
    processName: str | None = None
    target: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.DetonationBehaviourDetails"
