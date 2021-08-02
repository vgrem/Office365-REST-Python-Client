from office365.outlook.calendar.attendee import Attendee
from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.outlook.calendar.emailAddress import EmailAddress
from office365.outlook.calendar.event import Event
from office365.entity_collection import EntityCollection
from office365.outlook.mail.itemBody import ItemBody
from office365.runtime.client_value_collection import ClientValueCollection


class EventCollection(EntityCollection):
    """Event's collection"""

    def __init__(self, context, resource_path=None):
        super(EventCollection, self).__init__(context, Event, resource_path)

    def add(self, subject, body, start, end, attendees):
        """
        :param list[str] attendees: The collection of attendees emails for the event.
        :param datetime.datetime end: The date, time, and time zone that the event ends.
             By default, the end time is in UTC.
        :param datetime.datetime start: The date, time, and time zone that the event starts.
            By default, the start time is in UTC.
        :param str body: The body of the message associated with the event. It can be in HTML format.
        :param str subject: The text of the event's subject line.
        :rtype: Event
        """
        return super(EventCollection, self).add(
            subject=subject,
            body=ItemBody(body, "HTML"),
            start=DateTimeTimeZone.parse(start),
            end=DateTimeTimeZone.parse(end),
            attendees=
            ClientValueCollection(Attendee, [Attendee(EmailAddress(v), attendee_type="required") for v in attendees])
        )
