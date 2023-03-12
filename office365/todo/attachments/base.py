from office365.entity import Entity


class AttachmentBase(Entity):
    """Represents an abstract base type for an attachment. You can add related content to a todoTask in the form
    of an attachment."""

    @property
    def content_type(self):
        """The MIME type."""
        return self.properties.get("contentType", None)
