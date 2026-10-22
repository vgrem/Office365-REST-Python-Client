from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.directory.permissions.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue
from office365.runtime.types.odata_property import odata


@dataclass
class PlannerChecklistItem(ClientValue):
    """The plannerChecklistItem resource represents an item in the checklist of a task.
    The checklist on a task is represented by the checklistItems object.

    Args:
        title (str|None): The title of the checklist.
    """

    title: str | None = None

    isChecked: bool | None = None

    # Graph fills these two in and rejects them on write.
    lastModifiedBy: IdentitySet = field(
        default_factory=IdentitySet, metadata=odata(name="lastModifiedBy", readonly=True)
    )

    lastModifiedDateTime: datetime | None = field(
        default=None, metadata=odata(name="lastModifiedDateTime", readonly=True)
    )

    orderHint: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PlannerChecklistItem"
