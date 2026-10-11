from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.directory.users.identity import UserIdentity
from office365.intune.print.jobprocessingstate import PrintJobProcessingState
from office365.runtime.client_value import ClientValue


@dataclass
class ArchivedPrintJob(ClientValue):
    acquiredByPrinter: bool | None = None
    acquiredDateTime: datetime | None = None
    completionDateTime: datetime | None = None
    copiesPrinted: int | None = None
    createdBy: UserIdentity = field(default_factory=UserIdentity)
    createdDateTime: datetime | None = None
    id: str | None = None
    printerId: str | None = None
    printerName: str | None = None
    processingState: PrintJobProcessingState = PrintJobProcessingState.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ArchivedPrintJob"
