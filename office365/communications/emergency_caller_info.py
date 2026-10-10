from __future__ import annotations

from dataclasses import dataclass, field

from office365.outlook.mail.location import Location
from office365.runtime.client_value import ClientValue


@dataclass
class EmergencyCallerInfo(ClientValue):
    displayName: str | None = None
    location: Location = field(default_factory=Location)
    phoneNumber: str | None = None
    tenantId: str | None = None
    upn: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EmergencyCallerInfo"
