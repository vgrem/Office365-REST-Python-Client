from office365.entity_collection import EntityCollection
from office365.onedrive.driveItemVersion import DriveItemVersion


class DriveItemVersionCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(DriveItemVersionCollection, self).__init__(context, DriveItemVersion, resource_path)
