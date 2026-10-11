from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from office365.communications.onlinemeetings.provider_type import (
    OnlineMeetingProviderType,
)
from office365.directory.extensions.extended_property import (
    MultiValueLegacyExtendedProperty,
    SingleValueLegacyExtendedProperty,
)
from office365.directory.extensions.extension import Extension
from office365.directory.permissions.require_permission import require_permission
from office365.entity_collection import EntityCollection
from office365.outlook.calendar.attendees.attendee import Attendee
from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.outlook.calendar.events.sensitivity import Sensitivity
from office365.outlook.calendar.meetingtimes.freebusystatus import FreeBusyStatus
from office365.outlook.calendar.response_status import ResponseStatus
from office365.outlook.item import OutlookItem
from office365.outlook.mail.attachments.collection import AttachmentCollection
from office365.outlook.mail.body_type import BodyType
from office365.outlook.mail.item_body import ItemBody
from office365.outlook.mail.location import Location
from office365.outlook.mail.messages.eventtype import EventType
from office365.outlook.mail.patterned_recurrence import PatternedRecurrence
from office365.outlook.mail.recipient import Recipient
from office365.outlook.mail.recurrence_pattern import RecurrencePattern
from office365.outlook.mail.recurrence_range import RecurrenceRange
from office365.outlook.mail.recurrencepatterntype import RecurrencePatternType
from office365.outlook.mail.recurrencerangetype import RecurrenceRangeType
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.communications.onlinemeetings.online_meeting_info import (
        OnlineMeetingInfo,
    )
    from office365.outlook.calendar.events.event import Event


class Event(OutlookItem):
    """An event in a user calendar, or the default calendar of a Microsoft 365 group."""

    def set_recurrence(
        self,
        pattern_type: RecurrencePatternType = RecurrencePatternType.weekly,
        interval: int = 1,
        days_of_week: list[str] | None = None,
        range_type: RecurrenceRangeType = RecurrenceRangeType.numbered,
        occurrences: int = 4,
        start_date: date | None = None,
    ) -> Self:
        if (
            pattern_type
            in (
                RecurrencePatternType.weekly,
                RecurrencePatternType.relativeMonthly,
                RecurrencePatternType.relativeYearly,
            )
            and not days_of_week
        ):
            raise ValueError(f"days_of_week is required for pattern_type={pattern_type}")
        self.set_property(
            "recurrence",
            PatternedRecurrence(
                pattern=RecurrencePattern(
                    type=pattern_type,
                    daysOfWeek=ClientValueCollection(str, days_of_week),
                    interval=interval,
                ),
                range=RecurrenceRange(
                    type=range_type,
                    numberOfOccurrences=occurrences,
                    startDate=start_date,
                ),
            ),
        )
        return self

    @require_permission(delegated=["Calendars.ReadWrite"])
    def accept(self, send_response, comment=None):
        """Accept the specified event in a user calendar.

        Args:
            send_response (bool): true if a response is to be sent to the organizer; otherwise, false.
            comment (str): Text included in the response.
        """
        payload = {"SendResponse": send_response, "Comment": comment}
        qry = ServiceOperationQuery(self, "accept", None, payload)
        self.context.add_query(qry)
        return self

    @require_permission(delegated=["Calendars.ReadWrite"])
    def cancel(self, comment=None):
        """This action allows the organizer of a meeting to send a cancellation message and cancel the event.

        The action moves the event to the Deleted Items folder. The organizer can also cancel an occurrence
        of a recurring meeting by providing the occurrence event ID.
        An attendees calling this action gets an error (HTTP 400 Bad Request), with the following error message:
        Your request can't be completed. You need to be an organizer to cancel a meeting.

        Args:
            comment (str): Text included in the response.
        """
        payload = {"Comment": comment}
        qry = ServiceOperationQuery(self, "cancel", None, payload)
        self.context.add_query(qry)
        return self

    @require_permission(delegated=["Calendars.ReadWrite"])
    def decline(self, proposed_new_time=None, send_response=True, comment=None):
        """Decline invitation to the specified event in a user calendar.

        If the event allows proposals for new times, on declining the event, an invitee can choose to suggest
        an alternative time by including the proposedNewTime parameter. For more information on how to propose a time,
        and how to receive and accept a new time proposal, see Propose new meeting times.

        Args:
            proposed_new_time (office365.outlook.calendar.time_slot.TimeSlot): An alternate date/time proposed by
              an invitee for a meeting request to start and end. Valid only for events that allow new time proposals.
              Setting this parameter requires setting sendResponse to true. Optional.
            send_response (bool): true if a response is to be sent to the organizer; otherwise, false.
            comment (str): Text included in the response.
        """
        payload = {"ProposedNewTime": proposed_new_time, "SendResponse": send_response, "Comment": comment}
        qry = ServiceOperationQuery(self, "decline", None, payload)
        self.context.add_query(qry)
        return self

    @require_permission(delegated=["Calendars.ReadWrite"])
    def dismiss_reminder(self):
        """Dismiss a reminder that has been triggered for an event in a user calendar."""
        qry = ServiceOperationQuery(self, "dismissReminder")
        self.context.add_query(qry)
        return self

    @require_permission(delegated=["Calendars.ReadWrite"], application=["Calendars.ReadWrite"])
    def permanent_delete(self):
        """
        Permanently delete an event and place it in the purges folder in the dumpster in the user's mailbox.
        Email clients such as outlook or outlook on the web can't access permanently deleted items.
        Unless there's a hold set on the mailbox, the items are permanently deleted after a set period of time.
        """
        qry = ServiceOperationQuery(self, "permanentDelete")
        self.context.add_query(qry)
        return self

    @property
    def allow_new_time_proposals(self) -> Optional[bool]:
        """
        true if the meeting organizer allows invitees to propose a new time when responding; otherwise, false.
        Optional. Default is true.
        """
        return self.properties.get("allowNewTimeProposals", None)

    @property
    def has_attachments(self) -> Optional[bool]:
        """Set to true if the event has attachments."""
        return self.properties.get("hasAttachments", None)

    @property
    def hide_attendees(self) -> Optional[bool]:
        """
        When set to true, each attendee only sees themselves in the meeting request and meeting Tracking list.
        Default is false.
        """
        return self.properties.get("hideAttendees", None)

    @property
    def ical_uid(self) -> Optional[str]:
        """
        A unique identifier for an event across calendars. This ID is different for each occurrence in a recurring
        series.
        """
        return self.properties.get("iCalUId", None)

    @property
    def importance(self) -> Optional[str]:
        """The importance of the event. The possible values are: low, normal, high."""
        return self.properties.get("importance", None)

    @property
    def is_all_day(self) -> Optional[bool]:
        """
        Set to true if the event lasts all day. If true, regardless of whether it's a single-day or multi-day event,
        start and end time must be set to midnight and be in the same time zone.
        """
        return self.properties.get("isAllDay", None)

    @property
    def is_cancelled(self) -> Optional[bool]:
        """
        Set to true if the event has been canceled.
        """
        return self.properties.get("isCancelled", None)

    @property
    def is_draft(self) -> Optional[bool]:
        """
        Set to true if the user has updated the meeting in Outlook but hasn't sent the updates to attendees.
        Set to false if all changes are sent, or if the event is an appointment without any attendees.
        """
        return self.properties.get("isDraft", None)

    @property
    def is_online_meeting(self) -> Optional[bool]:
        """
        True if this event has online meeting information
        (that is, onlineMeeting points to an onlineMeetingInfo resource), false otherwise.
        Default is false (onlineMeeting is null). Optional.
        After you set isOnlineMeeting to true, Microsoft Graph initializes onlineMeeting.
        Subsequently, Outlook ignores any further changes to isOnlineMeeting, and the meeting remains available online.
        """
        return self.properties.get("isOnlineMeeting", None)

    @property
    def is_organizer(self) -> Optional[bool]:
        """
        Set to true if the calendar owner (specified by the owner property of the calendar) is the organizer of
        the event (specified by the organizer property of the event). It also applies if a delegate organized the
        event on behalf of the owner.
        """
        return self.properties.get("isOrganizer", None)

    @property
    def is_reminder_on(self) -> Optional[bool]:
        """
        Set to true if an alert is set to remind the user of the event.
        """
        return self.properties.get("isReminderOn", None)

    @property
    def start(self):
        """The date, time, and time zone that the event starts. By default, the start time is in UTC."""
        return self.properties.get("start", DateTimeTimeZone())

    @start.setter
    def start(self, value):
        """Sets the date, time, and time zone that the event starts. By default, the start time is in UTC.

        Args:
            value (datetime.datetime):
        """
        self.set_property("start", DateTimeTimeZone.parse(value))

    @property
    def end(self):
        """The date, time, and time zone that the event starts. By default, the start time is in UTC."""
        return self.properties.get("end", DateTimeTimeZone())

    @end.setter
    def end(self, value):
        """Sets the date, time, and time zone that the event starts. By default, the start time is in UTC.

        Args:
            value (datetime.datetime):
        """
        self.set_property("end", DateTimeTimeZone.parse(value))

    @odata(name="singleValueExtendedProperties")
    @property
    def single_value_extended_properties(self) -> EntityCollection[SingleValueLegacyExtendedProperty]:
        """The collection of single-value extended properties defined for the event."""
        return self.properties.get(
            "singleValueExtendedProperties",
            EntityCollection(
                self.context,
                SingleValueLegacyExtendedProperty,
                ResourcePath("singleValueExtendedProperties", self.resource_path),
            ),
        )

    @odata(name="multiValueExtendedProperties")
    @property
    def multi_value_extended_properties(self) -> EntityCollection[MultiValueLegacyExtendedProperty]:
        """The collection of multi-value extended properties defined for the event."""
        return self.properties.get(
            "multiValueExtendedProperties",
            EntityCollection(
                self.context,
                MultiValueLegacyExtendedProperty,
                ResourcePath("multiValueExtendedProperties", self.resource_path),
            ),
        )

    @property
    def body(self):
        """The body of the message associated with the event. It can be in HTML or text format."""
        return self.properties.get("body", ItemBody())

    @body.setter
    def body(self, value):
        """Sets The body of the message associated with the event. It can be in HTML or text format."""
        self.set_property("body", ItemBody(value, BodyType.html))

    @property
    def body_preview(self) -> Optional[str]:
        """The preview of the message associated with the event. It is in text format."""
        return self.properties.get("bodyPreview", None)

    @property
    def reminder_minutes_before_start(self) -> Optional[int]:
        """The number of minutes before the event start time that the reminder alert occurs."""
        return self.properties.get("reminderMinutesBeforeStart", None)

    @property
    def response_requested(self) -> Optional[bool]:
        """Default is true, which represents the organizer would like an invitee to send a response to the event."""
        return self.properties.get("responseRequested", None)

    @odata(name="responseStatus")
    @property
    def response_status(self) -> Optional[str]:
        """Indicates the type of response sent in response to an event message."""
        return self.properties.get("responseStatus", ResponseStatus())

    @property
    def series_master_id(self) -> Optional[str]:
        """The ID for the recurring series master item, if this event is part of a recurring series."""
        return self.properties.get("seriesMasterId", None)

    @property
    def subject(self) -> Optional[str]:
        """The text of the event's subject line."""
        return self.properties.get("subject", None)

    @subject.setter
    def subject(self, value: str) -> None:
        """Sets The text of the event's subject line."""
        self.set_property("subject", value)

    @property
    def location(self):
        """The location of the event."""
        return self.properties.get("location", Location())

    @property
    def transaction_id(self) -> Optional[str]:
        """
        A custom identifier specified by a client app for the server to avoid redundant POST operations in case of
        client retries to create the same event. This is useful when low network connectivity causes the client to
        time out before receiving a response from the server for the client's prior create-event request.
        After you set transactionId when creating an event, you cannot change transactionId in a subsequent update.
        This property is only returned in a response payload if an app has set it
        """
        return self.properties.get("transactionId", None)

    @property
    def type(self) -> Optional[str]:
        """
        The event type. Possible values are: singleInstance, occurrence, exception, seriesMaster
        """
        return self.properties.get("type", None)

    @property
    def web_link(self) -> Optional[str]:
        """
        The URL to open the event in Outlook on the web.

        Outlook on the web opens the event in the browser if you are signed in to your mailbox. Otherwise, Outlook
        on the web prompts you to sign in.

        This URL cannot be accessed from within an iFrame.
        """
        return self.properties.get("webLink", None)

    @property
    def calendar(self):
        """The calendar that contains the event. Navigation property. Read-only."""
        from office365.outlook.calendar.calendar import Calendar

        return self.properties.get("calendar", Calendar(self.context, ResourcePath("calendar", self.resource_path)))

    @property
    def attendees(self):
        """The collection of attendees for the event."""
        return self.properties.setdefault("attendees", ClientValueCollection(Attendee))

    @property
    def attachments(self):
        """The collection of fileAttachment and itemAttachment attachments for the event."""
        return self.properties.get(
            "attachments", AttachmentCollection(self.context, ResourcePath("attachments", self.resource_path))
        )

    @property
    def extensions(self) -> EntityCollection[Extension]:
        """The collection of open extensions defined for the event. Nullable."""
        return self.properties.get(
            "extensions", EntityCollection(self.context, Extension, ResourcePath("extensions", self.resource_path))
        )

    @property
    def instances(self):
        """The occurrences of a recurring series, if the event is a series master. This property includes occurrences
        that are part of the recurrence pattern, and exceptions that have been modified, but does not include
        occurrences that have been cancelled from the series"""
        from office365.outlook.calendar.events.collection import EventCollection

        return self.properties.get(
            "instances", EventCollection(self.context, ResourcePath("instances", self.resource_path))
        )

    @odata(name="cancelledOccurrences")
    @property
    def cancelled_occurrences(self) -> StringCollection:
        """Gets the cancelledOccurrences property"""
        return self.properties.get("cancelledOccurrences", StringCollection(None))

    @property
    def locations(self) -> ClientValueCollection[Location]:
        """Gets the locations property"""
        return self.properties.get("locations", ClientValueCollection[Location](Location))

    @odata(name="onlineMeetingProvider")
    @property
    def online_meeting_provider(self) -> OnlineMeetingProviderType:
        """Gets the onlineMeetingProvider property"""
        return self.properties.get("onlineMeetingProvider", OnlineMeetingProviderType.unknown)

    @property
    def online_meeting_url(self) -> Optional[str]:
        """Gets the onlineMeetingUrl property"""
        return self.properties.get("onlineMeetingUrl", None)

    @property
    def organizer(self) -> Recipient:
        """Gets the organizer property"""
        return self.properties.get("organizer", Recipient())

    @property
    def original_end_time_zone(self) -> Optional[str]:
        """Gets the originalEndTimeZone property"""
        return self.properties.get("originalEndTimeZone", None)

    @odata(name="originalStart")
    @property
    def original_start(self) -> datetime:
        """Gets the originalStart property"""
        return self.properties.get("originalStart", datetime.min)

    @property
    def original_start_time_zone(self) -> Optional[str]:
        """Gets the originalStartTimeZone property"""
        return self.properties.get("originalStartTimeZone", None)

    @property
    def recurrence(self) -> PatternedRecurrence:
        """Gets the recurrence property"""
        return self.properties.get("recurrence", PatternedRecurrence())

    @property
    def sensitivity(self) -> Sensitivity:
        """Gets the sensitivity property"""
        return self.properties.get("sensitivity", Sensitivity.normal)

    @odata(name="showAs")
    @property
    def show_as(self) -> FreeBusyStatus:
        """Gets the showAs property"""
        return self.properties.get("showAs", FreeBusyStatus.unknown)

    @property
    def type_(self) -> EventType:
        """Gets the type property"""
        return self.properties.get("type", EventType.singleInstance)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Event"

    @property
    def online_meeting(self) -> OnlineMeetingInfo:
        """Gets the onlineMeeting property"""
        from office365.communications.onlinemeetings.online_meeting_info import (
            OnlineMeetingInfo,
        )

        return self.properties.get("onlineMeeting", OnlineMeetingInfo())

    @property
    def exception_occurrences(self) -> EntityCollection[Event]:
        """Gets the exceptionOccurrences property"""
        from office365.outlook.calendar.events.event import Event

        return self.properties.get(
            "exceptionOccurrences",
            EntityCollection[Event](self.context, Event, ResourcePath("exceptionOccurrences", self.resource_path)),
        )
