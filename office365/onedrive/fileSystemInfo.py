from office365.runtime.client_value_object import ClientValueObject


class FileSystemInfo(ClientValueObject):
    """The FileSystemInfo resource contains properties that are reported by the device's local file system for the
    local version of an item. """

    def __init__(self, json=None):
        super(FileSystemInfo, self).__init__()
        self.createdDateTime = json.get('createdDateTime', None)
        self.lastAccessedDateTime = json.get('lastAccessedDateTime', None)
        self.lastModifiedDateTime = json.get('lastModifiedDateTime', None)
