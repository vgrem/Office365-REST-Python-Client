from office365.graph.onedrive.driveItem import DriveItem
from office365.graph.resource_path_url import ResourcePathUrl
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path import ResourcePath


class DriveItemCollection(ClientObjectCollection):
    """Drive items's collection"""

    def __init__(self, context, resource_path=None):
        super(DriveItemCollection, self).__init__(context, DriveItem, resource_path)

    def get_by_id(self, _id):
        """Retrieve DriveItem by id"""
        return DriveItem(self.context,
                         ResourcePath(_id, self.resource_path))

    def get_by_url(self, url):
        """Retrieve DriveItem by url"""
        return DriveItem(self.context,
                         ResourcePathUrl(url, self.resource_path))
