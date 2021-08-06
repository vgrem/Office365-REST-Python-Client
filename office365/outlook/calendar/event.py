from office365.entity_collection import EntityCollection
from office365.outlook.calendar.attendee import Attendee
from office365.directory.extensions.extension import Extension
from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.outlook.calendar.emailAddress import EmailAddress
from office365.outlook.mail.attachment_collection import AttachmentCollection
from office365.outlook.mail.item import Item
from office365.outlook.mail.itemBody import ItemBody
from office365.outlook.mail.location import Location
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.resource_path import ResourcePath


class Event(Item):
    """An event in a user calendar, or the default calendar of a Microsoft 365 group."""

    @property
    def start(self):
        """
        The date, time, and time zone that the event starts. By default, the start time is in UTC.
        """
        return self.get_property("start", DateTimeTimeZone())

    @start.setter
    def start(self, value):
        """
        Sets the date, time, and time zone that the event starts. By default, the start time is in UTC.
        """
        self.set_property("start", DateTimeTimeZone.parse(value))

    @property
    def end(self):
        """
        The date, time, and time zone that the event starts. By default, the start time is in UTC.
        """
        return self.get_property("end", DateTimeTimeZone())

    @end.setter
    def end(self, value):
        """
        Sets the date, time, and time zone that the event starts. By default, the start time is in UTC.
        """
        self.set_property("end", DateTimeTimeZone.parse(value))

    @property
    def body(self):
        """
        The body of the message associated with the event. It can be in HTML or text format.
        """
        return self.get_property("body", ItemBody())

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
        return self.get_property('calendar',
                                 Calendar(self.context, ResourcePath("calendar", self.resource_path)))

    @property
    def attendees(self):
        """The collection of attendees for the event."""
        return self.get_property('attendees',
                                 ClientValueCollection(Attendee))

    @attendees.setter
    def attendees(self, value):
        """Sets the collection of attendees for the event.

        :type value: list[str]
        """
        self.set_property('attendees',
                          ClientValueCollection(Attendee,
                                                [Attendee(EmailAddress(v), attendee_type="required") for v in value]))

    @property
    def attachments(self):
        """The collection of fileAttachment and itemAttachment attachments for the event. """
        return self.get_property('attachments',
                                 AttachmentCollection(self.context, ResourcePath("attachments", self.resource_path)))

    @property
    def extensions(self):
        """The collection of open extensions defined for the event. Nullable."""
        return self.get_property('extensions',
                                 EntityCollection(self.context, Extension,
                                                  ResourcePath("extensions", self.resource_path)))

    @property
    def instances(self):
        """The collection of open extensions defined for the event. Nullable."""
        return self.get_property('instances',
                                 EntityCollection(self.context, Event, ResourcePath("instances", self.resource_path)))
