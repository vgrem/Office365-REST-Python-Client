from office365.runtime.client_value import ClientValue


class FolderView(ClientValue):
    """The FolderView resource provides or sets recommendations on the user-experience of a folder."""

    def __init__(self, sortBy =None, sortOrder=None, viewType=None):
        super(FolderView, self).__init__()
        self.sortBy = sortBy
        self.sortOrder = sortOrder
        self.viewType = viewType
