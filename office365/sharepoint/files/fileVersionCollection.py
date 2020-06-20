from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.files.fileVersion import FileVersion


class FileVersionCollection(ClientObjectCollection):
    """Represents a collection of FileVersion."""
    def __init__(self, context, resource_path=None):
        super(FileVersionCollection, self).__init__(context, FileVersion, resource_path)
