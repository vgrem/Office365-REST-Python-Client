from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, cast

from office365.directory.permissions.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue
from office365.runtime.odata.json_format import ODataJsonFormat


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

    def to_json(self, json_format: Optional[ODataJsonFormat] = None) -> Dict[str, Any]:
        """Serializes the checklist item.

        ``lastModifiedBy`` and ``lastModifiedDateTime`` are server-managed;
        Graph rejects them on write, so they are omitted.
        """
        json = cast("Dict[str, Any]", super().to_json(json_format))
        json.pop("lastModifiedBy", None)
        json.pop("lastModifiedDateTime", None)
        return json
