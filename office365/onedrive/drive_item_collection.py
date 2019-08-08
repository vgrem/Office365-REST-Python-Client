from office365.onedrive.drive_item import DriveItem
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path_entity import ResourcePathEntity


class DriveItemCollection(ClientObjectCollection):
    """Drive items's collection"""

    def __init__(self, context, resource_path=None):
        super(DriveItemCollection, self).__init__(context, DriveItem, resource_path)

    def get_by_id(self, _id):
        """Retrieve DriveItem by unique identifier"""
        return DriveItem(self.context,
                         ResourcePathEntity(self.context, self.resource_path, _id))
