from __future__ import annotations

from dataclasses import dataclass

from office365.intune.print.taskprocessingstate import PrintTaskProcessingState
from office365.runtime.client_value import ClientValue


@dataclass
class PrintTaskStatus(ClientValue):
    description: str | None = None
    state: PrintTaskProcessingState = PrintTaskProcessingState.pending

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrintTaskStatus"
