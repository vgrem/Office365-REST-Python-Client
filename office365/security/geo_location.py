from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class GeoLocation(ClientValue):
    city: str | None = None
    countryName: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    state: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.GeoLocation"
