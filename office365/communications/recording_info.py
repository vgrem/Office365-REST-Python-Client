from __future__ import annotations

from dataclasses import dataclass, field

from office365.communications.calls.recordingstatus import RecordingStatus
from office365.directory.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue


@dataclass
class RecordingInfo(ClientValue):
    initiator: IdentitySet = field(default_factory=IdentitySet)
    recordingStatus: RecordingStatus = RecordingStatus.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RecordingInfo"
