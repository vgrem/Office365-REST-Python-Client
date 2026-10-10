from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.communications.callrecords.pstn_call_duration_source import (
    PstnCallDurationSource,
)
from office365.runtime.client_value import ClientValue


@dataclass
class PstnCallLogRow(ClientValue):
    callDurationSource: PstnCallDurationSource = PstnCallDurationSource.microsoft
    calleeNumber: str | None = None
    callerNumber: str | None = None
    callId: str | None = None
    callType: str | None = None
    charge: float | None = None
    conferenceId: str | None = None
    connectionCharge: float | None = None
    currency: str | None = None
    destinationContext: str | None = None
    destinationName: str | None = None
    duration: int | None = None
    endDateTime: datetime | None = None
    id: str | None = None
    inventoryType: str | None = None
    licenseCapability: str | None = None
    operator: str | None = None
    startDateTime: datetime | None = None
    tenantCountryCode: str | None = None
    usageCountryCode: str | None = None
    userDisplayName: str | None = None
    userId: str | None = None
    userPrincipalName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.PstnCallLogRow"
