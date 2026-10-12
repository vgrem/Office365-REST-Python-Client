from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, cast

from office365.directory.permissions.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue
from office365.runtime.odata.json_format import ODataJsonFormat


@dataclass
class PlannerAssignment(ClientValue):
    assignedBy: IdentitySet = field(default_factory=IdentitySet)
    assignedDateTime: datetime | None = None
    orderHint: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PlannerAssignment"

    def to_json(self, json_format: Optional[ODataJsonFormat] = None) -> Dict[str, Any]:
        """Serializes the assignment.

        ``assignedBy`` and ``assignedDateTime`` are server-managed; Graph
        rejects them on write, so they are omitted.
        """
        json = cast("Dict[str, Any]", super().to_json(json_format))
        json.pop("assignedBy", None)
        json.pop("assignedDateTime", None)
        return json
