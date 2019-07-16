from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.listitem import ListItem


class ListItemCollection(ClientObjectCollection):
    """List Item collection"""
    def __init__(self, context, resource_path=None):
        super(ListItemCollection, self).__init__(context, ListItem, resource_path)
