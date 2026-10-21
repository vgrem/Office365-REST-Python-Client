from __future__ import annotations

from dataclasses import dataclass

from office365.outlook.calendar.attendees.base import AttendeeBase
from office365.outlook.calendar.meetingtimes.time_slot import TimeSlot
from office365.outlook.calendar.response_status import ResponseStatus


@dataclass
class Attendee(AttendeeBase):
    """An event attendees. This can be a person or resource such as a meeting room or equipment,
    that has been set up as a resource on the Exchange server for the tenant."""

    proposedNewTime: TimeSlot | None = None
    status: ResponseStatus | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Attendee"
