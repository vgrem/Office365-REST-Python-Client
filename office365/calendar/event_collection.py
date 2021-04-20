from office365.calendar.attendee import Attendee
from office365.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.calendar.emailAddress import EmailAddress
from office365.calendar.event import Event
from office365.entity_collection import EntityCollection
from office365.mail.itemBody import ItemBody
from office365.runtime.client_value_collection import ClientValueCollection


class EventCollection(EntityCollection):
    """Event's collection"""
    def __init__(self, context, resource_path=None):
        super(EventCollection, self).__init__(context, Event, resource_path)

    def add(self, subject, body, start, end, attendees_emails):
        """
        :param list[str] attendees_emails: The collection of attendees emails for the event.
        :param datetime.datetime end: The date, time, and time zone that the event ends.
             By default, the end time is in UTC.
        :param datetime.datetime start: The date, time, and time zone that the event starts.
            By default, the start time is in UTC.
        :param str body: The body of the message associated with the event. It can be in HTML format.
        :param str subject: The text of the event's subject line.
        :rtype: Event
        """
        attendees_list = [Attendee(EmailAddress(email), attendee_type="required") for email in attendees_emails]
        payload = {
            "subject": subject,
            "body": ItemBody(body, "HTML"),
            "start": DateTimeTimeZone.parse(start),
            "end": DateTimeTimeZone.parse(end),
            "attendees": ClientValueCollection(Attendee, attendees_list)
        }
        return self.add_from_json(payload)
