from office365.onedrive.listItem import ListItem
from office365.runtime.client_object_collection import ClientObjectCollection


class ListItemCollection(ClientObjectCollection):
    """Drive list item's collection"""

    def __init__(self, context, resource_path=None):
        super(ListItemCollection, self).__init__(context, ListItem, resource_path)
