from __future__ import annotations

from dataclasses import dataclass, field

from office365.communications.broadcast_meeting_caption_settings import (
    BroadcastMeetingCaptionSettings,
)
from office365.communications.broadcastmeetingaudience import BroadcastMeetingAudience
from office365.runtime.client_value import ClientValue


@dataclass
class BroadcastMeetingSettings(ClientValue):
    """Represents settings related to a live event in Microsoft Teams.

    Fields:
        allowedAudience: ...
        isAttendeeReportEnabled: ...
        isQuestionAndAnswerEnabled: ...
        isRecordingEnabled: ...
        isVideoOnDemandEnabled: ...
    """

    allowedAudience: BroadcastMeetingAudience | None = None
    isAttendeeReportEnabled: bool | None = None
    isQuestionAndAnswerEnabled: bool | None = None
    isRecordingEnabled: bool | None = None
    isVideoOnDemandEnabled: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BroadcastMeetingSettings"

    captions: BroadcastMeetingCaptionSettings = field(default_factory=BroadcastMeetingCaptionSettings)
