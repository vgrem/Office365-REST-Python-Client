from office365.runtime.client_value import ClientValue


class Folder(ClientValue):

    def __init__(self, childCount=None, view=None):
        """

        :param int childCount:
        :param office365.onedrive.folderView.FolderView view:
        """
        super().__init__()
        self.childCount = childCount
        self.view = view
