from office365.entity import Entity


class Attachment(Entity):
    """A file or item (contact, event or message) attached to an event or message."""

    @property
    def name(self):
        """
        The attachment's file name.
        :rtype: str or None
        """
        return self.properties.get("name", None)

    @name.setter
    def name(self, value):
        """
        Sets the attachment's file name.
        :type: value: str
        """
        self.set_property("name", value)

    @property
    def content_type(self):
        """
        :rtype: str or None
        """
        return self.properties.get("contentType", None)

    @content_type.setter
    def content_type(self, value):
        """
        :type: value: str
        """
        self.set_property("contentType", value)

    @property
    def size(self):
        """

        :rtype: int or None
        """
        return self.properties.get("size", None)

    @property
    def last_modified_date_time(self):
        """
        The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time.

        :rtype: int or None
        """
        return self.properties.get("lastModifiedDateTime", None)

