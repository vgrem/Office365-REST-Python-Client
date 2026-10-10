from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.directory.permissions.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue


@dataclass
class PlannerAssignment(ClientValue):
    assignedBy: IdentitySet = field(default_factory=IdentitySet)
    assignedDateTime: datetime | None = None
    orderHint: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PlannerAssignment"
