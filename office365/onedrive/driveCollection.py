from office365.onedrive.drive import Drive
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path import ResourcePath


class DriveCollection(ClientObjectCollection):
    """Drive's collection"""

    def __init__(self, context, resource_path=None):
        super(DriveCollection, self).__init__(context, Drive, resource_path)

    def __getitem__(self, key):
        """

        :param key: key is used to address a Drive resource by either an index in collection
        or by drive id
        :type key: int or str
        """
        if type(key) == int:
            return super(DriveCollection, self).__getitem__(key)
        return Drive(self.context, ResourcePath(key, self.resource_path))
