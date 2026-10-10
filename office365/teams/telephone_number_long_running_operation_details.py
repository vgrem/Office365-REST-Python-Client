from __future__ import annotations

from dataclasses import dataclass

from office365.onedrive.operations.longrunningoperationstatus import (
    LongRunningOperationStatus,
)
from office365.runtime.client_value import ClientValue


@dataclass
class TelephoneNumberLongRunningOperationDetails(ClientValue):
    resourceLocation: str | None = None
    status: LongRunningOperationStatus = LongRunningOperationStatus.notStarted
    statusDetail: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.teamsAdministration.TelephoneNumberLongRunningOperationDetails"
