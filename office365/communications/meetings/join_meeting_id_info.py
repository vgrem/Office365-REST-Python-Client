from __future__ import annotations

from dataclasses import dataclass

from office365.communications.meetings.info import MeetingInfo


@dataclass
class JoinMeetingIdMeetingInfo(MeetingInfo):
    """Contains information that allows you to join an existing meeting with a joinMeetingId and a passcode
    (if required). You can retrieve these properties from the Get onlineMeeting API."""

    joinMeetingId: str | None = None

    passcode: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.JoinMeetingIdMeetingInfo"
