from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class OsVersionCount(ClientValue):
    deviceCount: int | None = None
    lastUpdateDateTime: datetime | None = None
    osVersion: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OsVersionCount"
