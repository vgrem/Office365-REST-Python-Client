from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.pollable import PollableOperation

if TYPE_CHECKING:
    from office365.onedrive.operations.longrunningoperationstatus import (
        LongRunningOperationStatus,
    )


class Operation(PollableOperation, Entity):
    """"""

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def last_action_date_time(self) -> Optional[datetime]:
        """Gets the lastActionDateTime property"""
        return self.properties.get("lastActionDateTime", datetime.min)

    @property
    def status(self) -> LongRunningOperationStatus:
        """Gets the status property"""
        from office365.onedrive.operations.longrunningoperationstatus import (
            LongRunningOperationStatus,
        )

        return self.properties.get("status", LongRunningOperationStatus.notStarted)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.partners.billing.Operation"
