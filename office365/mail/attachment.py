from office365.entity import Entity


class Attachment(Entity):
    """A file or item (contact, event or message) attached to an event or message."""

    @property
    def content_type(self):
        """

        :rtype: str or None
        """
        return self.properties.get("contentType", None)

    @property
    def size(self):
        """

        :rtype: int or None
        """
        return self.properties.get("size", None)
