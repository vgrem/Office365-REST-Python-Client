from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.onedrive.operations.longrunningoperationstatus import (
    LongRunningOperationStatus,
)
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.pollable import PollableOperation

if TYPE_CHECKING:
    from office365.teams.telephone_number_long_running_operation_details import (
        TelephoneNumberLongRunningOperationDetails,
    )


class TelephoneNumberLongRunningOperation(PollableOperation, Entity):
    @property
    def created_date_time(self) -> Optional[str]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", None)

    @property
    def status(self) -> LongRunningOperationStatus:
        """Gets the status property"""
        return self.properties.get("status", LongRunningOperationStatus.notStarted)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.teamsAdministration.TelephoneNumberLongRunningOperation"

    @property
    def numbers(self) -> ClientValueCollection[TelephoneNumberLongRunningOperationDetails]:
        """Gets the numbers property"""
        from office365.teams.telephone_number_long_running_operation_details import (
            TelephoneNumberLongRunningOperationDetails,
        )

        return self.properties.get(
            "numbers",
            ClientValueCollection[TelephoneNumberLongRunningOperationDetails](
                TelephoneNumberLongRunningOperationDetails
            ),
        )
