from office365.runtime.client_value import ClientValue


class ListItemCreationInformation(ClientValue):

    def __init__(self, leafName=None, folderUrl=None, underlyingObjectType=None):
        """
        Specifies the properties of the new list item.

        :param int underlyingObjectType: Specifies whether the new list item is a file or a folder.
        :param str leafName: Specifies the name of the new list item. It MUST be the name of the file if the parent
            list of the list item is a document library.
        :param str folderUrl: Specifies the folder for the new list item. It MUST be NULL, empty, a server-relative
            URL, or an absolute URL. If the value is a server-relative URL or an absolute URL, it MUST be under the root
            folder of the list.



        """
        super().__init__("SP")
        self.FolderUrl = folderUrl
        self.LeafName = leafName
        self.UnderlyingObjectType = underlyingObjectType
