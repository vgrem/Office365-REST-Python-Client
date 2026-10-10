from __future__ import annotations

from dataclasses import dataclass

from office365.communications.calls.rejectreason import RejectReason
from office365.runtime.client_value import ClientValue


@dataclass
class RejectJoinResponse(ClientValue):
    reason: RejectReason = RejectReason.none

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RejectJoinResponse"
