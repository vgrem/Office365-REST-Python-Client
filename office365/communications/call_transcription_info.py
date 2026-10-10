from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.communications.calls.transcriptionstate import CallTranscriptionState


@dataclass
class CallTranscriptionInfo(ClientValue):
    lastModifiedDateTime: datetime | None = None
    state: CallTranscriptionState = CallTranscriptionState.notStarted

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CallTranscriptionInfo"
