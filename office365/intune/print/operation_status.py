from __future__ import annotations

from dataclasses import dataclass

from office365.intune.print.operationprocessingstate import (
    PrintOperationProcessingState,
)
from office365.runtime.client_value import ClientValue


@dataclass
class PrintOperationStatus(ClientValue):
    description: str | None = None
    state: PrintOperationProcessingState = PrintOperationProcessingState.notStarted

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrintOperationStatus"
