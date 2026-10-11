from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.pollable import PollableOperation

if TYPE_CHECKING:
    from office365.intune.print.operation_status import PrintOperationStatus


class PrintOperation(PollableOperation, Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def status(self) -> PrintOperationStatus:
        """Gets the status property"""
        from office365.intune.print.operation_status import PrintOperationStatus

        return self.properties.get("status", PrintOperationStatus())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrintOperation"
