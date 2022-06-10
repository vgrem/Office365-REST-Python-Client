from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.listitems.listitem import ListItem


class ListItemCollection(BaseEntityCollection):
    """List Item collection"""
    def __init__(self, context, resource_path=None):
        super(ListItemCollection, self).__init__(context, ListItem, resource_path)
