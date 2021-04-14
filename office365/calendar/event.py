from office365.mail.item import Item
from office365.runtime.resource_path import ResourcePath


class Event(Item):
    """An event in a user calendar, or the default calendar of a Microsoft 365 group."""

    @property
    def id(self):
        return self.properties.get("id", None)

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
