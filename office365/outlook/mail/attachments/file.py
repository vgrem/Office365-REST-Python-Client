from office365.outlook.mail.attachments.attachment import Attachment


class FileAttachment(Attachment):
    """A file (such as a text file or Word document) attached to a user event, message, or post."""

    @property
    def content_id(self):
        """
        The ID of the attachment in the Exchange store.

        :rtype: str or None
        """
        return self.properties.get("contentId", None)

    @property
    def content_location(self):
        """
        :rtype: str or None
        """
        return self.properties.get("content_location", None)

    @property
    def content_bytes(self):
        """
        The base64-encoded contents of the file.

        :rtype: str or None
        """
        return self.properties.get("contentBytes", None)

    @content_bytes.setter
    def content_bytes(self, value):
        """
        Sets the base64-encoded contents of the file.
        """
        self.set_property("contentBytes", value)
