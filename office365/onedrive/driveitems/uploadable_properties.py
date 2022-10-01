from office365.runtime.client_value import ClientValue


class DriveItemUploadableProperties(ClientValue):
    """The driveItemUploadableProperties resource represents an item being uploaded when creating an upload session."""

    def __init__(self):
        super(DriveItemUploadableProperties, self).__init__()
        self.fileSystemInfo = None
        self.name = None
        self.description = None
        self._fileSize = None

    @property
    def file_size(self):
        """Provides an expected file size to perform a quota check prior to upload. Only on OneDrive Personal."""
        return self._fileSize
