from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.outlook.mail.messages.message import Message
from office365.outlook.mail.patterned_recurrence import PatternedRecurrence
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.communications.meetings.messagetype import MeetingMessageType
    from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
    from office365.outlook.mail.location import Location
    from office365.outlook.mail.messages.eventtype import EventType


class EventMessage(Message):
    """A message that represents a meeting request, cancellation, or response (which can be one of the following:
    acceptance, tentative acceptance, or decline)."""

    @odata(name="event", navigation=True)
    @property
    def event(self):
        """The event associated with the event message. The assumption for attendees or room resources is that
        the Calendar Attendant is set to automatically update the calendar with an event when meeting request event
        messages arrive. Navigation property. Read-only."""
        from office365.outlook.calendar.events.event import Event

        return self.properties.get("event", Event(self.context, ResourcePath("event", self.resource_path)))

    @property
    def patterned_recurrence(self) -> PatternedRecurrence:
        """"""
        return self.properties.get("patternedRecurrence", PatternedRecurrence())

    @odata(name="endDateTime")
    @property
    def end_date_time(self) -> DateTimeTimeZone:
        """Gets the endDateTime property"""
        from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone

        return self.properties.get("endDateTime", DateTimeTimeZone())

    @odata(name="isAllDay")
    @property
    def is_all_day(self) -> Optional[bool]:
        """Gets the isAllDay property"""
        return self.properties.get("isAllDay", None)

    @odata(name="isDelegated")
    @property
    def is_delegated(self) -> Optional[bool]:
        """Gets the isDelegated property"""
        return self.properties.get("isDelegated", None)

    @odata(name="isOutOfDate")
    @property
    def is_out_of_date(self) -> Optional[bool]:
        """Gets the isOutOfDate property"""
        return self.properties.get("isOutOfDate", None)

    @odata(name="location")
    @property
    def location(self) -> Location:
        """Gets the location property"""
        from office365.outlook.mail.location import Location

        return self.properties.get("location", Location())

    @odata(name="meetingMessageType")
    @property
    def meeting_message_type(self) -> MeetingMessageType:
        """Gets the meetingMessageType property"""
        from office365.communications.meetings.messagetype import MeetingMessageType

        return self.properties.get("meetingMessageType", MeetingMessageType.none)

    @odata(name="recurrence")
    @property
    def recurrence(self) -> PatternedRecurrence:
        """Gets the recurrence property"""
        from office365.outlook.mail.patterned_recurrence import PatternedRecurrence

        return self.properties.get("recurrence", PatternedRecurrence())

    @odata(name="startDateTime")
    @property
    def start_date_time(self) -> DateTimeTimeZone:
        """Gets the startDateTime property"""
        from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone

        return self.properties.get("startDateTime", DateTimeTimeZone())

    @odata(name="type")
    @property
    def type(self) -> EventType:
        """Gets the type property"""
        from office365.outlook.mail.messages.eventtype import EventType

        return self.properties.get("type", EventType.singleInstance)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EventMessage"
