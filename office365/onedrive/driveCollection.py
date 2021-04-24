from office365.entity_collection import EntityCollection
from office365.onedrive.drive import Drive


class DriveCollection(EntityCollection):
    """Drive's collection"""

    def __init__(self, context, resource_path=None):
        super(DriveCollection, self).__init__(context, Drive, resource_path)

    def __getitem__(self, key):
        """

        :param key: key is used to address a Drive resource by either an index in collection
        or by drive id
        :type key: int or str
        :rtype: Drive
        """
        return super(DriveCollection, self).__getitem__(key)
