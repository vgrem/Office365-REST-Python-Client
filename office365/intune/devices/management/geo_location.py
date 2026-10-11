from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class DeviceGeoLocation(ClientValue):
    altitude: float | None = None
    heading: float | None = None
    horizontalAccuracy: float | None = None
    lastCollectedDateTime: datetime | None = None
    latitude: float | None = None
    longitude: float | None = None
    speed: float | None = None
    verticalAccuracy: float | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceGeoLocation"
