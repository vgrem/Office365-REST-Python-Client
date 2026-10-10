from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


@dataclass
class PrinterLocation(ClientValue):
    altitudeInMeters: int | None = None
    building: str | None = None
    city: str | None = None
    countryOrRegion: str | None = None
    floor: str | None = None
    floorDescription: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    organization: StringCollection = field(default_factory=StringCollection)
    postalCode: str | None = None
    roomDescription: str | None = None
    roomName: str | None = None
    site: str | None = None
    stateOrProvince: str | None = None
    streetAddress: str | None = None
    subdivision: StringCollection = field(default_factory=StringCollection)
    subunit: StringCollection = field(default_factory=StringCollection)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrinterLocation"
