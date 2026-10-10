from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from datetime import timedelta


@dataclass
class TraceRouteHop(ClientValue):
    hopCount: int | None = None
    ipAddress: str | None = None
    roundTripTime: timedelta | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.TraceRouteHop"
