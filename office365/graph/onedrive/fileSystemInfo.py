from office365.runtime.client_value_object import ClientValueObject


class FileSystemInfo(ClientValueObject):
    """The FileSystemInfo resource contains properties that are reported by the device's local file system for the
    local version of an item. """

    def __init__(self):
        super(FileSystemInfo, self).__init__()
        self.createdDateTime = None
        self.lastAccessedDateTime = None
        self.lastModifiedDateTime = None
