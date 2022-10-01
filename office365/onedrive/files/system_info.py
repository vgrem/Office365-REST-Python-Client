from office365.runtime.client_value import ClientValue


class FileSystemInfo(ClientValue):
    """The FileSystemInfo resource contains properties that are reported by the device's local file system for the
    local version of an item. """

    def __init__(self, created_date_time=None):
        """
        :param str created_date_time: The UTC date and time the file was created on a client.

        """
        super(FileSystemInfo, self).__init__()
        self.createdDateTime = created_date_time
        self.lastAccessedDateTime = None
        self.lastModifiedDateTime = None
