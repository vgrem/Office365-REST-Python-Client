from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class AttendanceInterval(ClientValue):
    durationInSeconds: int | None = None
    joinDateTime: datetime | None = None
    leaveDateTime: datetime | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttendanceInterval"
