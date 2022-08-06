from office365.runtime.paths.entity import EntityPath
from office365.runtime.paths.resource_path import ResourcePath


class RootPath(EntityPath):
    """Resource path for OneDrive path-based addressing"""

    def __init__(self, parent=None, collection=None):
        super(RootPath, self).__init__("root", parent, collection)

    @property
    def collection(self):
        if self._collection is None:
            self._collection = ResourcePath("items", self.parent)
        return self._collection
