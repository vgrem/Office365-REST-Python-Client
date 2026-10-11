from __future__ import annotations

from enum import Enum


class InvestigationState(Enum):
    unknown = "0"
    terminated = "1"
    successfullyRemediated = "2"
    benign = "4"
    failed = "8"
    partiallyRemediated = "16"
    running = "32"
    pendingApproval = "64"
    pendingResource = "128"
    queued = "512"
    innerFailure = "1024"
    preexistingAlert = "2048"
    unsupportedOs = "4056"
    unsupportedAlertType = "8192"
    suppressedAlert = "16384"
    partiallyInvestigated = "32768"
    terminatedByUser = "65536"
    terminatedBySystem = "131072"
    unknownFutureValue = "262144"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.InvestigationState"
