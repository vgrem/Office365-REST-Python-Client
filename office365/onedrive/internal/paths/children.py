from office365.runtime.paths.resource_path import ResourcePath


class ChildrenPath(ResourcePath):
    """Resource path for OneDrive children addressing"""

    def __init__(self, parent, collection_name="items"):
        """
        :param str collection_name: Resolved path name
        """
        super(ChildrenPath, self).__init__("children", parent)
        self._collection_name = collection_name

    def normalize(self, name, parent=None, inplace=False):
        from office365.onedrive.internal.paths.root import RootPath
        if isinstance(self.parent, RootPath):
            path = self.parent.normalize(name, parent, inplace)
            return super(ChildrenPath, self).normalize(path.name, path.parent, inplace)
        else:
            return super(ChildrenPath, self).normalize(name, ResourcePath(self._collection_name, self.parent), inplace)
