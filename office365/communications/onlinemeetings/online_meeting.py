from office365.entity import Entity


class OnlineMeeting(Entity):
    """
    Contains information about a meeting, including the URL used to join a meeting,
    the attendees list, and the description.
    """

    @property
    def subject(self):
        """The subject of the online meeting."""
        return self.properties.get("subject", None)

    @property
    def join_web_url(self):
        """The join URL of the online meeting. Read-only."""
        return self.properties.get("joinWebUrl", None)
