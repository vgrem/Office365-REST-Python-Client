from office365.runtime.client_value_object import ClientValueObject


class FileCreationInformation(ClientValueObject):
    """Represents properties that can be set when creating a file by using the FileCollection.Add method."""

    def __init__(self):
        super(FileCreationInformation, self).__init__()
        self._url = None
        self._overwrite = False
        self._content = None

    @property
    def content(self):
        """Gets the binary content of the file."""
        return self._content

    @content.setter
    def content(self, value):
        """Sets the binary content of the file."""
        self._content = value

    @property
    def overwrite(self):
        """Indicates whether to overwrite an existing file with the same name and in the same location
        as the one being added."""
        return self._overwrite

    @property
    def url(self):
        """The URL of the file."""
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @overwrite.setter
    def overwrite(self, value):
        self._overwrite = value
