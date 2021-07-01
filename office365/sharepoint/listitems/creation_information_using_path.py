from office365.runtime.client_value import ClientValue


class ListItemCreationInformationUsingPath(ClientValue):

    def __init__(self, leaf_name, object_type, folder_path=None):
        """

        :type leaf_name: str
        :type object_type: int
        :type folder_path: office365.sharepoint.types.resource_path.ResourcePath
        """
        super(ListItemCreationInformationUsingPath, self).__init__()
        self.FolderPath = folder_path
        self.LeafName = leaf_name
        self.UnderlyingObjectType = object_type
