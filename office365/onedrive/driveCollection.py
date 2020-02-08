from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path import ResourcePath
from office365.onedrive.drive import Drive


class DriveCollection(ClientObjectCollection):
    """Drive's collection"""

    def __init__(self, context, resource_path=None):
        super(DriveCollection, self).__init__(context, Drive, resource_path)

    def get_by_id(self, url):
        """Retrieve DriveItem by url"""
        return Drive(self.context,
                     ResourcePath(url, self.resourcePath))
