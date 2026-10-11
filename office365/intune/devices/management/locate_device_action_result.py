from __future__ import annotations

from dataclasses import dataclass, field

from office365.intune.devices.management.geo_location import DeviceGeoLocation
from office365.runtime.client_value import ClientValue


@dataclass
class LocateDeviceActionResult(ClientValue):
    deviceLocation: DeviceGeoLocation = field(default_factory=DeviceGeoLocation)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.LocateDeviceActionResult"
