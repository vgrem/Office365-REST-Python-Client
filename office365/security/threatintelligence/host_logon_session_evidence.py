from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.security.device_evidence import DeviceEvidence
from office365.security.user_evidence import UserEvidence


@dataclass
class HostLogonSessionEvidence(ClientValue):
    account: UserEvidence = field(default_factory=UserEvidence)
    endUtcDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    host: DeviceEvidence = field(default_factory=DeviceEvidence)
    sessionId: str | None = None
    startUtcDateTime: datetime | None = field(default_factory=lambda: datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.HostLogonSessionEvidence"
