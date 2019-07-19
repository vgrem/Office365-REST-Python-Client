from office365.onedrive.drive_item import DriveItem
from office365.runtime.client_object_collection import ClientObjectCollection


class DriveItemCollection(ClientObjectCollection):
    """Drive items's collection"""

    def __init__(self, context, resource_path=None):
        super(DriveItemCollection, self).__init__(context, DriveItem, resource_path)
