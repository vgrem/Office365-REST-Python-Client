from office365.runtime.client_value import ClientValue


class Folder(ClientValue):
    """
    The Folder resource groups folder-related data on an item into a single structure.
    DriveItems with a non-null folder facet are containers for other DriveItems.
    """

    def __init__(self, child_count=None, view=None):
        """
        :param int child_count: Number of children contained immediately within this container.
        :param office365.onedrive.folderView.FolderView view: A collection of properties defining the recommended
             view for the folder.
        """
        super(Folder, self).__init__()
        self.childCount = child_count
        self.view = view
