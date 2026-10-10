from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.communications.calls.mediastate import MediaState


@dataclass
class CallMediaState(ClientValue):
    audio: MediaState = MediaState.active

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CallMediaState"
