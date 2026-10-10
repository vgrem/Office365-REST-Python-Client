from __future__ import annotations

from dataclasses import dataclass

from office365.communications.calls.tone import Tone
from office365.runtime.client_value import ClientValue


@dataclass
class ToneInfo(ClientValue):
    sequenceId: int | None = None
    tone: Tone = Tone.tone0

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ToneInfo"
