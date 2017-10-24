from office365.runtime.client_value_object import ClientValueObject


class AttachmentfileCreationInformation(ClientValueObject):
    """Represents properties that can be set when creating a file by using the AttachmentFiles.Add method."""

    def __init__(self, filename=None, content=None):
        super(AttachmentfileCreationInformation, self).__init__()
        self._filename = filename
        self._content = content

    @property
    def content(self):
        """Gets the binary content of the file."""
        return self._content

    @content.setter
    def content(self, value):
        """Sets the binary content of the file."""
        self._content = value

    @property
    def filename(self):
        """The URL of the file."""
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value
