from office365.entity_collection import EntityCollection
from office365.onedrive.sharedDriveItem import SharedDriveItem


class SharedDriveItemCollection(EntityCollection):
    """sharedDriveItem's collection"""

    def __init__(self, context, resource_path=None):
        super(SharedDriveItemCollection, self).__init__(context, SharedDriveItem, resource_path)
