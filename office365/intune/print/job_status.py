from __future__ import annotations

from dataclasses import dataclass, field

from office365.intune.print.jobprocessingstate import PrintJobProcessingState
from office365.intune.print.jobstatedetail import PrintJobStateDetail
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class PrintJobStatus(ClientValue):
    description: str | None = None
    details: ClientValueCollection[PrintJobStateDetail] = field(
        default_factory=lambda: ClientValueCollection(PrintJobStateDetail)
    )
    isAcquiredByPrinter: bool | None = None
    state: PrintJobProcessingState = PrintJobProcessingState.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrintJobStatus"
