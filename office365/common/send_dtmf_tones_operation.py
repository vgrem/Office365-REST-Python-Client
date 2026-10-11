from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.pollable import PollableOperation

if TYPE_CHECKING:
    from office365.communications.operations.senddtmfcompletionreason import (
        SendDtmfCompletionReason,
    )


class SendDtmfTonesOperation(PollableOperation, Entity):
    @property
    def completion_reason(self) -> SendDtmfCompletionReason:
        """Gets the completionReason property"""
        from office365.communications.operations.senddtmfcompletionreason import (
            SendDtmfCompletionReason,
        )

        return self.properties.get("completionReason", SendDtmfCompletionReason.unknown)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SendDtmfTonesOperation"
