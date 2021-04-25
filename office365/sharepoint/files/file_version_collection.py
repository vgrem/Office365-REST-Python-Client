from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.files.file_version import FileVersion


class FileVersionCollection(BaseEntityCollection):
    """Represents a collection of FileVersion."""
    def __init__(self, context, resource_path=None):
        super(FileVersionCollection, self).__init__(context, FileVersion, resource_path)
