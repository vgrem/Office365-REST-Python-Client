from office365.runtime.paths.resource_path import ResourcePath


class EntityPath(ResourcePath):
    def __init__(self, key=None, parent=None, collection=None):
        """
        :param str or None key: Entity key
        :param ResourcePath or None collection:
        """
        super(EntityPath, self).__init__(key, parent)
        self._collection = collection

    @property
    def collection(self):
        from office365.onedrive.internal.paths.children import ChildrenPath

        if self._collection is None:
            if isinstance(self.parent, ChildrenPath):
                self._collection = self.parent.collection
            else:
                self._collection = self.parent
        return self._collection

    @property
    def segment(self):
        return str(self._key or "<key>")

    def patch(self, key):
        """
        Patches path
        :type key: str or None
        """
        self._key = key
        self._parent = self.collection
        self.__class__ = EntityPath
        return self
