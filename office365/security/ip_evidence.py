from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.security.geo_location import GeoLocation
from office365.security.stream import Stream


@dataclass
class IpEvidence(ClientValue):
    countryLetterCode: str | None = None
    ipAddress: str | None = None
    stream: Stream = field(default_factory=Stream)
    location: GeoLocation = field(default_factory=GeoLocation)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.IpEvidence"
