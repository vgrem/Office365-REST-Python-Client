from office365.entity_collection import EntityCollection
from office365.onedrive.listItem import ListItem


class ListItemCollection(EntityCollection):
    """Drive list item's collection"""

    def __init__(self, context, resource_path=None):
        super(ListItemCollection, self).__init__(context, ListItem, resource_path)
