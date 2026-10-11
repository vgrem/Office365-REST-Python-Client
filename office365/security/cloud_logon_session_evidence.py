from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.security.user_evidence import UserEvidence


@dataclass
class CloudLogonSessionEvidence(ClientValue):
    browser: str | None = None
    deviceName: str | None = None
    operatingSystem: str | None = None
    previousLogonDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    protocol: str | None = None
    sessionId: str | None = None
    startUtcDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    userAgent: str | None = None
    account: UserEvidence = field(default_factory=UserEvidence)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.CloudLogonSessionEvidence"
