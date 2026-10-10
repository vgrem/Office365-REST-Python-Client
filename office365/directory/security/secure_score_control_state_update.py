from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class SecureScoreControlStateUpdate(ClientValue):
    assignedTo: str | None = None
    comment: str | None = None
    state: str | None = None
    updatedBy: str | None = None
    updatedDateTime: datetime | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SecureScoreControlStateUpdate"
