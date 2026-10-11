from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.pollable import PollableOperation

if TYPE_CHECKING:
    from office365.directory.delegatedadmin.relationshipoperationtype import (
        DelegatedAdminRelationshipOperationType,
    )
    from office365.onedrive.operations.longrunningoperationstatus import (
        LongRunningOperationStatus,
    )


class DelegatedAdminRelationshipOperation(PollableOperation, Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def data(self) -> Optional[str]:
        """Gets the data property"""
        return self.properties.get("data", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def operation_type(self) -> DelegatedAdminRelationshipOperationType:
        """Gets the operationType property"""
        from office365.directory.delegatedadmin.relationshipoperationtype import (
            DelegatedAdminRelationshipOperationType,
        )

        return self.properties.get(
            "operationType", DelegatedAdminRelationshipOperationType.delegatedAdminAccessAssignmentUpdate
        )

    @property
    def status(self) -> LongRunningOperationStatus:
        """Gets the status property"""
        from office365.onedrive.operations.longrunningoperationstatus import (
            LongRunningOperationStatus,
        )

        return self.properties.get("status", LongRunningOperationStatus.notStarted)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DelegatedAdminRelationshipOperation"
