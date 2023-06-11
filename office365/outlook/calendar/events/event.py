from office365.delta_collection import DeltaCollection
from office365.directory.extensions.extended_property import SingleValueLegacyExtendedProperty, \
    MultiValueLegacyExtendedProperty
from office365.entity_collection import EntityCollection
from office365.directory.extensions.extension import Extension
from office365.outlook.calendar.attendees.attendee import Attendee
from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.outlook.calendar.email_address import EmailAddress
from office365.outlook.item import OutlookItem
from office365.outlook.mail.attachments.collection import AttachmentCollection
from office365.outlook.mail.item_body import ItemBody
from office365.outlook.mail.location import Location
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath


class Event(OutlookItem):
    """An event in a user calendar, or the default calendar of a Microsoft 365 group."""

    def accept(self, send_response, comment=None):
        """
        Accept the specified event in a user calendar.

        :param bool send_response: true if a response is to be sent to the organizer; otherwise, false.
        :param str comment: Text included in the response.
        """
        payload = {
            "SendResponse": send_response,
            "Comment": comment
        }
        qry = ServiceOperationQuery(self, "accept", None, payload)
        self.context.add_query(qry)
        return self

    def cancel(self, comment=None):
        """
        This action allows the organizer of a meeting to send a cancellation message and cancel the event.

        The action moves the event to the Deleted Items folder. The organizer can also cancel an occurrence
        of a recurring meeting by providing the occurrence event ID.
        An attendees calling this action gets an error (HTTP 400 Bad Request), with the following error message:
            Your request can't be completed. You need to be an organizer to cancel a meeting.

        :param str comment: Text included in the response.
        """
        payload = {
            "Comment": comment
        }
        qry = ServiceOperationQuery(self, "cancel", None, payload)
        self.context.add_query(qry)
        return self

    def decline(self, proposed_new_time=None, send_response=True, comment=None):
        """
        Decline invitation to the specified event in a user calendar.

        If the event allows proposals for new times, on declining the event, an invitee can choose to suggest
        an alternative time by including the proposedNewTime parameter. For more information on how to propose a time,
        and how to receive and accept a new time proposal, see Propose new meeting times.

        :param office365.outlook.calendar.time_slot.TimeSlot proposed_new_time: An alternate date/time proposed by an
            invitee for a meeting request to start and end. Valid only for events that allow new time proposals.
            Setting this parameter requires setting sendResponse to true. Optional.
        :param bool send_response: true if a response is to be sent to the organizer; otherwise, false.
        :param str comment: Text included in the response.
        """
        payload = {
            "ProposedNewTime": proposed_new_time,
            "SendResponse": send_response,
            "Comment": comment
        }
        qry = ServiceOperationQuery(self, "decline", None, payload)
        self.context.add_query(qry)
        return self

    def dismiss_reminder(self):
        """
        Dismiss a reminder that has been triggered for an event in a user calendar.
        """
        qry = ServiceOperationQuery(self, "dismissReminder")
        self.context.add_query(qry)
        return self

    @property
    def start(self):
        """
        The date, time, and time zone that the event starts. By default, the start time is in UTC.

        :rtype: DateTimeTimeZone
        """
        return self.properties.get("start", DateTimeTimeZone())

    @start.setter
    def start(self, value):
        """
        Sets the date, time, and time zone that the event starts. By default, the start time is in UTC.

        :type value: datetime.datetime
        """
        self.set_property("start", DateTimeTimeZone.parse(value))

    @property
    def end(self):
        """
        The date, time, and time zone that the event starts. By default, the start time is in UTC.

        :rtype: DateTimeTimeZone
        """
        return self.properties.get("end", DateTimeTimeZone())

    @end.setter
    def end(self, value):
        """
        Sets the date, time, and time zone that the event starts. By default, the start time is in UTC.

        :type value: datetime.datetime
        """
        self.set_property("end", DateTimeTimeZone.parse(value))

    @property
    def single_value_extended_properties(self):
        """The collection of single-value extended properties defined for the event.
        """
        return self.properties.get('singleValueExtendedProperties',
                                 EntityCollection(self.context, SingleValueLegacyExtendedProperty,
                                                  ResourcePath("singleValueExtendedProperties", self.resource_path)))

    @property
    def multi_value_extended_properties(self):
        """The collection of multi-value extended properties defined for the event."""
        return self.properties.get('multiValueExtendedProperties',
                                   EntityCollection(self.context, MultiValueLegacyExtendedProperty,
                                                    ResourcePath("multiValueExtendedProperties", self.resource_path)))

    @property
    def body(self):
        """
        The body of the message associated with the event. It can be in HTML or text format.
        """
        return self.properties.get("body", ItemBody())

    @body.setter
    def body(self, value):
        """
        Sets The body of the message associated with the event. It can be in HTML or text format.
        """
        self.set_property("body", ItemBody(value, "HTML"))

    @property
    def body_preview(self):
        """
        The preview of the message associated with the event. It is in text format.
        :rtype: str or None
        """
        return self.properties.get("bodyPreview", None)

    @property
    def subject(self):
        """
        The text of the event's subject line.
        :rtype: str or None
        """
        return self.properties.get("subject", None)

    @subject.setter
    def subject(self, value):
        """
        Sets The text of the event's subject line.
        :type: str or None
        """
        self.set_property("subject", value)

    @property
    def location(self):
        """
        The location of the event.
        """
        return self.properties.get("location", Location())

    @property
    def web_link(self):
        """
        The URL to open the event in Outlook on the web.

        Outlook on the web opens the event in the browser if you are signed in to your mailbox. Otherwise, Outlook
        on the web prompts you to sign in.

        This URL cannot be accessed from within an iFrame.

        :rtype: str or None
        """
        return self.properties.get("webLink", None)

    @property
    def calendar(self):
        """The calendar that contains the event. Navigation property. Read-only."""
        from office365.outlook.calendar.calendar import Calendar
        return self.properties.get('calendar',
                                   Calendar(self.context, ResourcePath("calendar", self.resource_path)))

    @property
    def attendees(self):
        """The collection of attendees for the event."""
        return self.properties.setdefault('attendees', ClientValueCollection(Attendee))

    @property
    def attachments(self):
        """The collection of fileAttachment and itemAttachment attachments for the event. """
        return self.properties.get('attachments',
                                   AttachmentCollection(self.context, ResourcePath("attachments", self.resource_path)))

    @property
    def extensions(self):
        """The collection of open extensions defined for the event. Nullable."""
        return self.properties.get('extensions',
                                   EntityCollection(self.context, Extension,
                                                    ResourcePath("extensions", self.resource_path)))

    @property
    def instances(self):
        """The occurrences of a recurring series, if the event is a series master. This property includes occurrences
        that are part of the recurrence pattern, and exceptions that have been modified, but does not include
        occurrences that have been cancelled from the series"""
        from office365.outlook.calendar.events.collection import EventCollection
        return self.properties.get('instances',
                                   EventCollection(self.context, ResourcePath("instances", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "multiValueExtendedProperties": self.multi_value_extended_properties,
                "singleValueExtendedProperties": self.single_value_extended_properties
            }
            default_value = property_mapping.get(name, None)
        return super(Event, self).get_property(name, default_value)
