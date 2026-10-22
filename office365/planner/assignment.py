from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.directory.permissions.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue
from office365.runtime.types.odata_property import odata


@dataclass
class PlannerAssignment(ClientValue):
    """Who a task is assigned to, and when the service recorded the assignment."""

    # Graph fills these two in and rejects them on write.
    assignedBy: IdentitySet = field(default_factory=IdentitySet, metadata=odata(name="assignedBy", readonly=True))
    assignedDateTime: datetime | None = field(default=None, metadata=odata(name="assignedDateTime", readonly=True))
    orderHint: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PlannerAssignment"
