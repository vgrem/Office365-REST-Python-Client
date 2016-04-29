from client_object import ClientObject
from client.file_collection import FileCollection


class Folder(ClientObject):
    """Represents a folder in a SharePoint Web site."""

    @property
    def files(self):
        """Get a file collection"""
        if self.is_property_available('Files'):
            return self.properties["Files"]
        else:
            return FileCollection(self.context, "files", self.resource_path)
