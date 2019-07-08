from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.listitem import ListItem


class ListItemCollection(ClientObjectCollection):
    """List Item collection"""

    # The object type this collection holds
    item_type = ListItem
