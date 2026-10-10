from __future__ import annotations

from dataclasses import dataclass

from office365.communications.onlinemeetings.contentsharingdisabledreason import (
    OnlineMeetingContentSharingDisabledReason,
)
from office365.communications.onlinemeetings.videodisabledreason import (
    OnlineMeetingVideoDisabledReason,
)
from office365.runtime.client_value import ClientValue


@dataclass
class OnlineMeetingRestricted(ClientValue):
    """Indicates the reason or reasons media content from a participant is restricted."""

    contentSharingDisabled: OnlineMeetingContentSharingDisabledReason = (
        OnlineMeetingContentSharingDisabledReason.watermarkProtection
    )

    videoDisabled: OnlineMeetingVideoDisabledReason = OnlineMeetingVideoDisabledReason.watermarkProtection

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnlineMeetingRestricted"
