from office365.entity_collection import EntityCollection
from office365.onedrive.driveItem import DriveItem
from office365.runtime.resource_path import ResourcePath


class DriveItemCollection(EntityCollection):
    """Drive items's collection"""

    def __init__(self, context, resource_path=None):
        super(DriveItemCollection, self).__init__(context, DriveItem, resource_path)

    def get_by_id(self, _id):
        """Retrieve DriveItem by id"""
        return DriveItem(self.context, ResourcePath(_id, self.resource_path))
