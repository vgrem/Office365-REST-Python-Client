from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.communications.callrecords.failurestage import FailureStage


@dataclass
class FailureInfo(ClientValue):
    reason: str | None = None
    stage: FailureStage = FailureStage.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.FailureInfo"
