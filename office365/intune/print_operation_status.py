from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.intune.print.operationprocessingstate import (
        PrintOperationProcessingState,
    )


@dataclass
class PrintOperationStatus(ClientValue):
    description: str | None = None
    state: PrintOperationProcessingState = PrintOperationProcessingState.notStarted

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrintOperationStatus"
