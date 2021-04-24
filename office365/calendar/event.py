from office365.calendar.attendee import Attendee
from office365.directory.extension import ExtensionCollection
from office365.mail.attachment_collection import AttachmentCollection
from office365.mail.item import Item
from office365.mail.location import Location
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.resource_path import ResourcePath


class Event(Item):
    """An event in a user calendar, or the default calendar of a Microsoft 365 group."""

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
        from office365.calendar.calendar import Calendar
        return self.properties.get('calendar',
                                   Calendar(self.context, ResourcePath("calendar", self.resource_path)))

    @property
    def attendees(self):
        """The collection of attendees for the event."""
        return self.properties.get('attendees',
                                   ClientValueCollection(Attendee))

    @property
    def attachments(self):
        """The collection of fileAttachment and itemAttachment attachments for the event. """
        return self.properties.get('attachments',
                                   AttachmentCollection(self.context, ResourcePath("attachments", self.resource_path)))

    @property
    def extensions(self):
        """The collection of open extensions defined for the event. Nullable."""
        return self.properties.get('extensions',
                                   ExtensionCollection(self.context, ResourcePath("extensions", self.resource_path)))

    @property
    def instances(self):
        """The collection of open extensions defined for the event. Nullable."""
        from office365.calendar.event_collection import EventCollection
        return self.properties.get('instances',
                                   EventCollection(self.context, ResourcePath("instances", self.resource_path)))
