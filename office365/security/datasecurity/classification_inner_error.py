from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class ClassificationInnerError(ClientValue):
    activityId: str | None = None
    clientRequestId: str | None = None
    code: str | None = None
    errorDateTime: datetime | None = field(default_factory=lambda: datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ClassificationInnerError"
