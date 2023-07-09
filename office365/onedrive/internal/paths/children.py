from office365.runtime.paths.entity import EntityPath


class ChildrenPath(EntityPath):
    """Resource path for OneDrive children addressing"""

    def __init__(self, parent, collection=None):
        super(ChildrenPath, self).__init__("children", parent, collection)

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.parent.collection
        return self._collection
