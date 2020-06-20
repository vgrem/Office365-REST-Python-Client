from office365.runtime.clientValue import ClientValue


class ListItemCreationInformation(ClientValue):
    """Specifies the properties of the new list item."""

    def __init__(self):
        super().__init__()
        self.FolderUrl = None
        self.LeafName = None
        self.UnderlyingObjectType = None
