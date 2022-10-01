from office365.runtime.client_value import ClientValue


class FolderView(ClientValue):
    """The FolderView resource provides or sets recommendations on the user-experience of a folder."""

    def __init__(self, sort_by=None, sort_order=None, view_type=None):
        super(FolderView, self).__init__()
        self.sortBy = sort_by
        self.sortOrder = sort_order
        self.viewType = view_type
