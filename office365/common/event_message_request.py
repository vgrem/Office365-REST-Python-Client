from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.communications.meetings.requesttype import MeetingRequestType
    from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
    from office365.outlook.mail.location import Location


class EventMessageRequest(Entity):
    @property
    def allow_new_time_proposals(self) -> Optional[bool]:
        """Gets the allowNewTimeProposals property"""
        return self.properties.get("allowNewTimeProposals", None)

    @property
    def meeting_request_type(self) -> MeetingRequestType:
        """Gets the meetingRequestType property"""
        from office365.communications.meetings.requesttype import MeetingRequestType

        return self.properties.get("meetingRequestType", MeetingRequestType.none)

    @property
    def previous_end_date_time(self) -> DateTimeTimeZone:
        """Gets the previousEndDateTime property"""
        from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone

        return self.properties.get("previousEndDateTime", DateTimeTimeZone())

    @property
    def previous_location(self) -> Location:
        """Gets the previousLocation property"""
        from office365.outlook.mail.location import Location

        return self.properties.get("previousLocation", Location())

    @property
    def previous_start_date_time(self) -> DateTimeTimeZone:
        """Gets the previousStartDateTime property"""
        from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone

        return self.properties.get("previousStartDateTime", DateTimeTimeZone())

    @property
    def response_requested(self) -> Optional[bool]:
        """Gets the responseRequested property"""
        return self.properties.get("responseRequested", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EventMessageRequest"
