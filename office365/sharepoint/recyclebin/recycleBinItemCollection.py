from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.recyclebin.recycleBinItem import RecycleBinItem


class RecycleBinItemCollection(ClientObjectCollection):
    """Represents a collection of View resources."""

    def __init__(self, context, resource_path=None):
        super(RecycleBinItemCollection, self).__init__(context, RecycleBinItem, resource_path)
