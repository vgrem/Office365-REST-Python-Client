from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class DirectRoutingLogRow(ClientValue):
    """Represents a row of data in the direct routing call log. Each row maps to one call."""

    calleeNumber: str | None = None

    callEndSubReason: int | None = None

    callerNumber: str | None = None

    callType: str | None = None

    correlationId: str | None = None

    duration: int | None = None

    endDateTime: datetime | None = None

    failureDateTime: datetime | None = None

    finalSipCode: int | None = None

    finalSipCodePhrase: str | None = None

    id: str | None = None

    inviteDateTime: datetime | None = None

    mediaBypassEnabled: bool | None = None

    mediaPathLocation: str | None = None

    signalingLocation: str | None = None

    startDateTime: datetime | None = None

    successfulCall: bool | None = None

    trunkFullyQualifiedDomainName: str | None = None

    userDisplayName: str | None = None

    userId: str | None = None

    userPrincipalName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.DirectRoutingLogRow"
