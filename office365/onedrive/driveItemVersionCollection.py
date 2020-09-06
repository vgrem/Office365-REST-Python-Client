from office365.onedrive.driveItemVersion import DriveItemVersion
from office365.runtime.client_object_collection import ClientObjectCollection


class DriveItemVersionCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(DriveItemVersionCollection, self).__init__(context, DriveItemVersion, resource_path)
