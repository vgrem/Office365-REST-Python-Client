from onedrive.drive import Drive
from runtime.client_object_collection import ClientObjectCollection


class DriveCollection(ClientObjectCollection):
    """Drive's collection"""
    def __init__(self, context, resource_path=None):
        super(DriveCollection, self).__init__(context, Drive, resource_path)
