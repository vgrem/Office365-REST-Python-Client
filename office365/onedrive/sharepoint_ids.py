from office365.runtime.client_value import ClientValue


class SharePointIds(ClientValue):
    """The SharePointIds resource groups the various identifiers for an item stored in a SharePoint site or OneDrive
    for Business into a single structure. """

    def __init__(self, list_id=None, list_item_id=None, list_item_unique_id=None):
        """
        :param str list_id: The unique identifier (guid) for the item's list in SharePoint.
        :param str list_item_id: An integer identifier for the item within the containing list.
        :param str list_item_unique_id: The unique identifier (guid) for the item within OneDrive for Business
            or a SharePoint site.
        """
        self.listId = list_id
        self.listItemId = list_item_id
        self.listItemUniqueId = list_item_unique_id
