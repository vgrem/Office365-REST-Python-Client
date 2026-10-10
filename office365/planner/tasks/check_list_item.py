from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.directory.permissions.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue


@dataclass
class PlannerChecklistItem(ClientValue):
    """The plannerChecklistItem resource represents an item in the checklist of a task.
    The checklist on a task is represented by the checklistItems object.

    Args:
        title (str|None): The title of the checklist.
    """

    title: str | None = None

    isChecked: bool | None = None

    lastModifiedBy: IdentitySet = field(default_factory=IdentitySet)

    lastModifiedDateTime: datetime | None = None

    orderHint: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PlannerChecklistItem"
