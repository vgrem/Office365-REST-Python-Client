from office365.entity_collection import EntityCollection
from office365.onedrive.driveItem import DriveItem


class DriveItemCollection(EntityCollection):
    """Drive items's collection"""

    def __init__(self, context, resource_path=None):
        super(DriveItemCollection, self).__init__(context, DriveItem, resource_path)
