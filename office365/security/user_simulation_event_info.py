from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.security.attacksimulations.clicksource import ClickSource


@dataclass
class UserSimulationEventInfo(ClientValue):
    browser: str | None = None
    clickSource: ClickSource = ClickSource.unknown
    eventDateTime: datetime | None = None
    eventName: str | None = None
    ipAddress: str | None = None
    osPlatformDeviceDetails: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserSimulationEventInfo"
