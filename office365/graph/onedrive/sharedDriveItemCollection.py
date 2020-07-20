from office365.graph.onedrive.sharedDriveItem import SharedDriveItem
from office365.runtime.client_object_collection import ClientObjectCollection


class SharedDriveItemCollection(ClientObjectCollection):
    """sharedDriveItem's collection"""

    def __init__(self, context, resource_path=None):
        super(SharedDriveItemCollection, self).__init__(context, SharedDriveItem, resource_path)
